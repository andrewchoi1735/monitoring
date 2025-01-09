pipeline {
    agent any
    stages {
        stage('Clone Repository') {
            steps {
                script {
                    try {
                        sh 'git clone https://github.com/andrewchoi1735/monitoring.git'
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        throw e
                    }
                }
            }
        }
        stage('Pull Updates') {
            steps {
                script {
                    dir('monitoring/Othetak') {
                        try {
                            sh 'git pull'
                        } catch (Exception e) {
                            currentBuild.result = 'FAILURE'
                            throw e
                        }
                    }
                }
            }
        }
        stage('Run Python Script') {
            steps {
                script {
                    dir('monitoring/Othetak') {
                        try {
                            sh 'python3 main.py'
                        } catch (Exception e) {
                            currentBuild.result = 'FAILURE'
                            throw e
                        }
                    }
                }
            }
        }
    }
    post {
        failure {
            script {
                def currentTime = new Date().time / 1000
                echo "빌드 실패 시간: ${new Date(currentTime * 1000).format('yyyy-MM-dd HH:mm:ss')}"

                // Prometheus에 메트릭 전송
                sh "echo 'jenkins_build_fail_time{job_name=\"website_stat\"} ${currentTime}' | curl --data-binary @- http://localhost:9090/metrics/job/jenkins"
            }
        }
        success {
            echo "빌드 성공"
        }
    }
}
