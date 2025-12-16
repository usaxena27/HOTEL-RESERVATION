pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "project-cdab2309-f11d-4cf6-8b4"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages{
        stage('Cloning Github repo to Jenkins'){
            steps{
                script{
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/usaxena27/HOTEL-RESERVATION.git']])
                }
            }
        }

        stage('Setting up Virtual Environment and Installing Dependencies'){
            steps{
                script{
                    echo 'Setting up Virtual Environment and Installing Dependencies............'
                    sh '''
                        python3 -m venv ${VENV_DIR}
                        . ${VENV_DIR}/bin/activate
                        pip install --upgrade pip
                        pip install -e .
                        deactivate
                    '''
                }
            }
        }

        stage('Building and Pushing Docker Image to GCR'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Building and Pushing Docker Image to GCR.............'
                        sh '''
                            export PATH=$PATH:${GCLOUD_PATH}

                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                            gcloud config set project ${GCP_PROJECT}

                            gcloud auth configure-docker --quiet

                            docker build -t gcr.io/${GCP_PROJECT}/ml-project:${IMAGE_TAG} \
                                         -t gcr.io/${GCP_PROJECT}/ml-project:latest .

                            docker push gcr.io/${GCP_PROJECT}/ml-project:${IMAGE_TAG}
                            docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                        '''
                    }
                }
            }
        }

        stage('Deploy to Google Cloud Run'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Deploy to Google Cloud Run.............'
                        sh '''
                            export PATH=$PATH:${GCLOUD_PATH}

                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                            gcloud config set project ${GCP_PROJECT}

                            gcloud run deploy ml-project \
                                --image=gcr.io/${GCP_PROJECT}/ml-project:latest \
                                --platform=managed \
                                --region=us-central1 \
                                --allow-unauthenticated
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Build #${BUILD_NUMBER} successful! Image: gcr.io/${GCP_PROJECT}/ml-project:${BUILD_NUMBER}"
        }
        failure {
            echo "❌ Build #${BUILD_NUMBER} failed. Check logs above."
        }
        always {
            cleanWs()
        }
    }
}