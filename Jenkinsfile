
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
                        chmod 700 "$DOCKER_CONFIG"

                        trap 'rm -rf "$DOCKER_CONFIG"' EXIT

                        printf '{}' > "$DOCKER_CONFIG/config.json"
                        chmod 600 "$DOCKER_CONFIG/config.json"

                        echo "Docker config directory: $DOCKER_CONFIG"
                        echo "Docker config contents:"
                        cat "$DOCKER_CONFIG/config.json"

                        printf '%s' "$DOCKERHUB_TOKEN" | \
                        docker --config "$DOCKER_CONFIG" \
                            -H unix:///home/ideapad/.docker/desktop/docker.sock \
                            login docker.io \
                            --username "$DOCKERHUB_USERNAME" \
                            --password-stdin

                        docker --config "$DOCKER_CONFIG" \
                            -H unix:///home/ideapad/.docker/desktop/docker.sock \
                            push rahuldocker04/employee-management-api:v2

                        docker --config "$DOCKER_CONFIG" \
                            -H unix:///home/ideapad/.docker/desktop/docker.sock \
                            logout docker.io
                    '''
                }
            }
        }
    }
}
