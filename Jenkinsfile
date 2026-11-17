pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/sairamsolake/ai-tickets-app.git'
        BRANCH = 'main'
        DOCKER_USER = 'sairam2107'
        BACKEND_IMAGE = "${DOCKER_USER}/ai-ticket-classifier-backend"
        FRONTEND_IMAGE = "${DOCKER_USER}/ai-ticket-classifier-frontend"
        K8S_NAMESPACE = 'ai-tickets'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${BRANCH}", url: "${REPO_URL}"
            }
        }

        stage('Lint Backend (Ruff)') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m pip install --quiet --break-system-packages ruff || pip install --quiet ruff
                        ruff check .
                    '''
                }
            }
        }

        stage('Build & Push Docker Images') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

                        docker build -t ${BACKEND_IMAGE}:${BUILD_NUMBER} -t ${BACKEND_IMAGE}:latest ./backend
                        docker build -t ${FRONTEND_IMAGE}:${BUILD_NUMBER} -t ${FRONTEND_IMAGE}:latest ./frontend

                        docker push ${BACKEND_IMAGE}:${BUILD_NUMBER}
                        docker push ${BACKEND_IMAGE}:latest
                        docker push ${FRONTEND_IMAGE}:${BUILD_NUMBER}
                        docker push ${FRONTEND_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig-ai-tickets', variable: 'KUBECONFIG')]) {
                    sh '''
                        sed -i "s|image: ${BACKEND_IMAGE}:.*|image: ${BACKEND_IMAGE}:${BUILD_NUMBER}|g" k8s/07-backend-deployment.yaml
                        sed -i "s|image: ${FRONTEND_IMAGE}:.*|image: ${FRONTEND_IMAGE}:${BUILD_NUMBER}|g" k8s/09-frontend-deployment.yaml

                        kubectl apply -f k8s/

                        kubectl rollout status deployment/backend -n ${K8S_NAMESPACE} --timeout=120s
                        kubectl rollout status deployment/frontend -n ${K8S_NAMESPACE} --timeout=120s
                        kubectl rollout status deployment/db -n ${K8S_NAMESPACE} --timeout=120s
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
        failure {
            echo "Pipeline failed for build #${BUILD_NUMBER}. Check pods with: kubectl get pods -n ${K8S_NAMESPACE}"
        }
    }
}
