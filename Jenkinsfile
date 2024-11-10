pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'weather_image'
        REPO_URL = 'git@github.com:Kovalenkolex/weather_bot.git'
        BRANCH_NAME = 'dev'
        PROJECT_DIR = '/srv/weather_bot'
        TELEGRAM_BOT_TOKEN = credentials('TELEGRAM_BOT_TOKEN')
    }

    stages {
        stage('Clone Repository') {
            steps {
                dir("${PROJECT_DIR}") {
                    git branch: "${BRANCH_NAME}", url: "${REPO_URL}", credentialsId: "kovalenkolex"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t ${DOCKER_IMAGE} .'
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    sh '''
                    docker stop weather_bot || true
                    docker rm weather_bot || true
                    docker run --restart unless-stopped -d --name weather_bot -v /srv/weather_bot/sql:/sql -p 8081:80 ${DOCKER_IMAGE}
                    '''
                }
            }
        }
    }

    post {
        always {
            cleanWs() // Очистка рабочей директории после сборки
        }
    }
}