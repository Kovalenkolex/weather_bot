pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'weather_image' // Имя Docker-образа
        REPO_URL = 'https://github.com/Kovalenkolex/weather_bot.git' // URL твоего репозитория
        BRANCH_NAME = 'dev' // Ветка, с которой будем работать
        PROJECT_DIR = '/opt/weather_bot'
    }

    stages {
        stage('Clone Repository') {
            steps {
                dir("${PROJECT_DIR}") {
                    git branch: "${BRANCH_NAME}", url: "${REPO_URL}"
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
                    docker run --restart unless-stopped -d --name weather_bot -v /opt/weather_bot/sql:/sql -p 80:80 ${DOCKER_IMAGE}
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
