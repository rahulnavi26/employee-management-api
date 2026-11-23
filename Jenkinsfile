
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

                        export DOCKER_CONFIG=$(mktemp -d)
                        trap 'rm -rf "$DOCKER_CONFIG"' EXIT

                        printf '%s' "$DOCKERHUB_TOKEN" | \
                        docker -H unix:///home/ideapad/.docker/desktop/docker.sock \
                        login docker.io \
                        --username "$DOCKERHUB_USERNAME" \
                        --password-stdin

                        docker -H unix:///home/ideapad/.docker/desktop/docker.sock \
                        push rahuldocker04/employee-management-api:v2

                        docker -H unix:///home/ideapad/.docker/desktop/docker.sock \
                        logout docker.io
                    '''
                }
            }
        }
    }
}
