
pipeline {
    agent any

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
                        -t rahuldocker04/employee-management-api:v2 .
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

                echo "Logging in to Docker Hub..."

                printf '%s' "$DOCKERHUB_TOKEN" | \
                PATH="$DOCKER_CONFIG/bin" /usr/bin/docker \
                    --config "$DOCKER_CONFIG" \
                    -H unix:///home/ideapad/.docker/desktop/docker.sock \
                    login docker.io \
                    --username "$DOCKERHUB_USERNAME" \
                    --password-stdin

                echo "Pushing Docker image..."

                PATH="$DOCKER_CONFIG/bin" /usr/bin/docker \
                    --config "$DOCKER_CONFIG" \
                    -H unix:///home/ideapad/.docker/desktop/docker.sock \
                    push rahuldocker04/employee-management-api:v2

                echo "Docker image pushed successfully."
                        '''
        }
    }
        }
    }
}