pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/andrewchoi1735/monitoring.git', branch: 'main'
            }
        }
        stage('Run Specific File') {
            steps {
                sh 'chmod +x path/to/your_script.sh' // 실행 권한 부여
                sh './path/to/your_script.sh' // 파일 실행
            }
        }
    }
}
