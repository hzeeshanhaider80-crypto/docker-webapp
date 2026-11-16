
pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'zeeshan2007'
        APP_SERVER     = '172.31.18.97'
        IMAGE_NAME     = 'zeeshan2007/docker-webapp'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                dir('app') {
                    sh '''
                        set -e

                        python3 -m venv ../.venv
                        . ../.venv/bin/activate

                        python -m pip install --upgrade pip

                        python -m pip install \
                            -r requirements.txt \
                            -r requirements-dev.txt

                        python -c "import flask_wtf; print('Flask-WTF installed successfully')"

                        python -m pytest -v --junitxml=../test-results.xml
                    '''
                }
            }

            post {
                always {
                    junit allowEmptyResults: true,
                          testResults: 'test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            environment {
                SCANNER_HOME = tool 'sonar-scanner'
            }

            steps {
                withSonarQubeEnv('sonarqube') {
                    sh '''
                        $SCANNER_HOME/bin/sonar-scanner \
                          -Dsonar.projectKey=docker-webapp \
                          -Dsonar.sources=app \
                          -Dsonar.exclusions=app/test_*.py \
                          -Dsonar.tests=app \
                          -Dsonar.test.inclusions=app/test_*.py \
                          -Dsonar.python.version=3.12
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Trivy: Libraries') {
            steps {
                sh '''
                    trivy fs \
                      --scanners vuln \
                      --severity HIGH,CRITICAL \
                      --exit-code 0 app
                '''
            }
        }

        stage('Build Image') {
            steps {
                sh '''
                    docker build \
                      --build-arg APP_VERSION=${IMAGE_TAG} \
                      -t ${IMAGE_NAME}:${IMAGE_TAG} \
                      -t ${IMAGE_NAME}:latest \
                      app
                '''
            }
        }

        stage('Trivy: Image') {
            steps {
                sh '''
                    trivy image \
                      --severity CRITICAL \
                      --ignore-unfixed \
                      --exit-code 1 \
                      ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    sh '''
                        set -e

                        echo "$DH_TOKEN" | docker login \
                          -u "$DH_USER" \
                          --password-stdin

                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to App Server') {
            steps {
                sshagent(credentials: ['app-server-ssh']) {
                    sh '''
                        set -e

                        SSH="ssh -o StrictHostKeyChecking=no"
                        SCP="scp -o StrictHostKeyChecking=no"

                        $SSH ubuntu@${APP_SERVER} \
                          "mkdir -p ~/app/nginx ~/app/app"

                        $SCP docker-compose.yml \
                          ubuntu@${APP_SERVER}:~/app/

                        $SCP -r app \
                          ubuntu@${APP_SERVER}:~/app/

                        $SCP nginx/default.conf \
                          ubuntu@${APP_SERVER}:~/app/nginx/

                        $SSH ubuntu@${APP_SERVER} \
                          "cd ~/app && export WEB_IMAGE=${IMAGE_NAME}:${IMAGE_TAG} && docker compose pull && docker compose up -d --no-build --remove-orphans"
                    '''
                }
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    set -e

                    for i in $(seq 1 30); do
                        if curl -sf http://${APP_SERVER}/health; then
                            echo "Application is healthy"
                            exit 0
                        fi

                        sleep 2
                    done

                    echo "Application health check failed"
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo "Version ${IMAGE_TAG} is live!"
        }

        failure {
            echo "Build failed. Check the failed stage in Jenkins."
        }

        always {
            sh 'docker image prune -f || true'
        }
    }
}
