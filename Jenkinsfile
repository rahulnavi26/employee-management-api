pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    stages {

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv-ci
                    . .venv-ci/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . .venv-ci/bin/activate
                    python -m pytest -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker -H unix:///home/ideapad/.docker/desktop/docker.sock build \
                        -t employee-management-api:v2 \
                        -t rahuldocker04/employee-management-api:v2 \
                        -t rahuldocker04/employee-management-api:build-${BUILD_NUMBER} .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        set -eu

                        export DOCKER_CONFIG=$(mktemp -d)
                        mkdir -p "$DOCKER_CONFIG/bin"
                        chmod 700 "$DOCKER_CONFIG"
                        printf '{}' > "$DOCKER_CONFIG/config.json"
                        chmod 600 "$DOCKER_CONFIG/config.json"

                        trap 'rm -rf "$DOCKER_CONFIG"' EXIT

                        printf '%s' "$DOCKERHUB_TOKEN" | \
                        /usr/bin/docker \
                            --config "$DOCKER_CONFIG" \
                            -H unix:///home/ideapad/.docker/desktop/docker.sock \
                            login docker.io \
                            --username "$DOCKERHUB_USERNAME" \
                            --password-stdin

                        /usr/bin/docker \
                            --config "$DOCKER_CONFIG" \
                            -H unix:///home/ideapad/.docker/desktop/docker.sock \
                            push rahuldocker04/employee-management-api:v2

                        /usr/bin/docker \
                            --config "$DOCKER_CONFIG" \
                            -H unix:///home/ideapad/.docker/desktop/docker.sock \
                            push rahuldocker04/employee-management-api:build-${BUILD_NUMBER}

                        echo "Docker images pushed successfully."
                    '''
                }
            }
        }

        stage('Deploy to AWS EC2') {
            steps {
                sh '''
                    set -eu

                    IMAGE_TAG="build-${BUILD_NUMBER}"

                    ssh -o BatchMode=yes \
                        -o ConnectTimeout=10 \
                        ubuntu@13.51.233.6 \
                        "IMAGE_TAG=${IMAGE_TAG} bash -s" <<'REMOTE'

                    set -eu

                    IMAGE="rahuldocker04/employee-management-api:${IMAGE_TAG}"

                    echo "Capturing currently deployed image..."

                    OLD_IMAGE=$(docker inspect \
                        --format='{{.Image}}' employee-api 2>/dev/null || true)

                    echo "Pulling new application image..."
                    docker pull "$IMAGE"

                    echo "Removing previous container..."
                    docker rm -f employee-api 2>/dev/null || true

                    echo "Starting new application container..."

                    if ! docker run -d \
                        --name employee-api \
                        --restart unless-stopped \
                        -p 5000:5000 \
                        "$IMAGE"; then

                        echo "New container failed to start. Rolling back..."

                        if [ -n "$OLD_IMAGE" ]; then
                            docker run -d \
                                --name employee-api \
                                --restart unless-stopped \
                                -p 5000:5000 \
                                "$OLD_IMAGE"
                        fi

                        exit 1
                    fi

                    echo "Checking application health..."

                    HEALTHY=false

                    for attempt in $(seq 1 15); do
                        if curl -fsS http://localhost:5000/health >/dev/null; then
                            HEALTHY=true
                            break
                        fi

                        echo "Waiting for application... attempt $attempt"
                        sleep 2
                    done

                    if [ "$HEALTHY" = "true" ]; then
                        echo "Deployment successful!"
                        exit 0
                    fi

                    echo "Health check failed. Rolling back..."

                    docker logs --tail 50 employee-api || true
                    docker rm -f employee-api || true

                    if [ -n "$OLD_IMAGE" ]; then
                        docker run -d \
                            --name employee-api \
                            --restart unless-stopped \
                            -p 5000:5000 \
                            "$OLD_IMAGE"

                        echo "Previous application image restored."
                    else
                        echo "No previous image available for rollback."
                    fi

                    exit 1

REMOTE
                '''
            }
        }
    }
}
