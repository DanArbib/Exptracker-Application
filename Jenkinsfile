def new_version
pipeline {
    agent {
        label 'master'
    }

    options {
        timeout(time:10, unit: 'MINUTES')
        timestamps()
        buildDiscarder(logRotator(
            numToKeepStr: '15',
            artifactNumToKeepStr: '30')
        )
    }

    environment {
        // Networks
        JENKINS_NETWORK = 'jenkins_jenkins-net_test'
        APP_NETWORK = 'app-net'

        // App
        APP_NAME_COMPOSE = 'app'
        APP_DOCKERFILE = 'Dockerfile.app'
        APP_NAME = 'glivs-app'
        APP_PORT = 5000

        // Nginx
        NGINX_DOCKERFILE = 'Dockerfile.nginx'
        NGINX_NAME = 'nginx'

        // ECR
        REGION = 'ap-south-1'
        ECR_URI = '644435390668.dkr.ecr.ap-south-1.amazonaws.com/dan-portfolio-app'

        // Gitops repo
        GITOPS_REPO = 'git@gitlab.com:jenkins3190014/glivs-gitops.git'
        CHART_PATH = 'glivs/Chart.yaml'
        CHART_FOLDER = 'glivs-gitops'

        // S3 bucket
        S3_BUCKET_NAME = 'glivs-static'

    }
    stages {
        stage('Build') { // BUILD APPLICATION IMAGE
            when {
                anyOf {
                    branch 'main'
                    branch 'feature/*'
                }
            }
            steps {
                updateGitlabCommitStatus name: 'build', state: 'pending'
                echo 'Building docker image...'
                sh """
                    docker build -f ${APP_DOCKERFILE} -t ${APP_NAME}:${BUILD_NUMBER} .

                    # Nginx image for testing only
                    docker build -f ${NGINX_DOCKERFILE} -t ${NGINX_NAME}:${BUILD_NUMBER} .
                """
                updateGitlabCommitStatus name: 'build', state: 'success'
            }
        }
        stage('Unitest') { // RUN UNIT TEST
            steps {
                updateGitlabCommitStatus name: 'Unitest', state: 'pending'
                echo 'Running unitests...'

                updateGitlabCommitStatus name: 'Unitest', state: 'success'
            }
        }
        stage('E2E TESTS') { // RUN END TO END TESTS ON MAIN AND FEATURE
            when {
                anyOf {
                    branch 'main'
                    branch 'feature/*'
                }
            }
            steps {
                sh """
                    mv env.example .env
                    sed -i 's/#image_app:.*\$/image: ${APP_NAME_COMPOSE}:${BUILD_NUMBER}/' docker-compose.yml
                    sed -i 's/#image_nginx:.*\$/image: ${NGINX_NAME}:${BUILD_NUMBER}/' docker-compose.yml
                    docker compose up -d
                    docker network connect ${JENKINS_NETWORK} ${NGINX_NAME}
                    chmod +x ./tests/healthcheck.sh
                    chmod +x ./tests/e2e.sh
                    ./tests/healthcheck.sh ${NGINX_NAME} 30 5
                    ./tests/e2e.sh nginx
                """
            }
            post {
                always{
                    sh """
                        docker compose down --volumes --remove-orphans
                        docker network prune -f
                    """
                }
            }
        }
        stage('Versioning') { // SET VERSION FOR MAIN BRANCH
            when { 
                branch 'main'
            }
            steps {
                sshagent(credentials: ['gitlab_ssh']) {
                    script {

                        // Get commit message
                        def commit_msg = sh(script: "git log -1 --pretty=%B", returnStdout: true).trim()
                        echo "Commit Message: ${commit_msg}"

                        // Get last tag
                        def last_tag = sh(script: "git tag --list \'[0-9]*.[0-9]*.[0-9]*\' | sort -V | tail -n 1", returnStdout: true).trim()
                        echo "Last tag: ${last_tag}"

                        // Check if tag exists
                        if (last_tag == '') {
                            new_version = '1.0.0'
                        } else {
                            def (major, minor, patch) = last_tag.tokenize('.')
                            echo "Splited: ${major}, ${minor}, ${patch}"
                            patch = (patch.toInteger() + 1).toString()
                            new_version = "${major}.${minor}.${patch}"
                        }
                        echo "New version: ${new_version}"
                    }
                }
            }
        }
        stage('Publish') { // PUSH IMAGE TO ECR FOR MAIN COMMITS
            when { 
                branch 'main'
            }
            steps {
                updateGitlabCommitStatus name: 'publish', state: 'pending'
                echo "Pushing image to ECR..."
                sh """
                    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI
                    docker tag $APP_NAME:$BUILD_NUMBER $ECR_URI:${new_version}
                    docker push $ECR_URI:${new_version}
                """
                updateGitlabCommitStatus name: 'publish', state: 'success'
            }
        }
        stage('Deploy') { // CHANGE HELM CHART VERSION 
            when { 
                branch 'main'
            }
            steps {
                updateGitlabCommitStatus name: 'deploy', state: 'pending'
                sshagent(credentials: ['gitlab_ssh']) {
                    echo "Deploying..."
                    sh """
                        git clone ${GITOPS_REPO} ${APP_NAME}
                        yq -i '.appVersion = \"${new_version}\"' ${APP_NAME}/glivs/Chart.yaml
                        yq -i '.application.image.tag = \"${new_version}\"' ${APP_NAME}/glivs/values.yaml
                        git -C ${APP_NAME} add glivs/Chart.yaml
                        git -C ${APP_NAME} add glivs/values.yaml
                        git -C ${APP_NAME} commit -m "App version - ${new_version}"
                        git -C ${APP_NAME} push origin main
                    """
                updateGitlabCommitStatus name: 'deploy', state: 'success'
                }
            }
        }
        stage('Tagging') { // TAGGING MAIN COMMITS
            when { 
                branch 'main'
            }
            steps {
                echo "Tagging nnew version..."
                updateGitlabCommitStatus name: 'tagging', state: 'pending'
                sshagent(credentials: ['gitlab_ssh']) {
                    sh """
                        git clean -f -x
                        git tag ${new_version}
                        git push origin ${new_version}
                    """
                }
                updateGitlabCommitStatus name: 'tagging', state: 'success'
            }
        }
    }
    post {
        always {
            echo 'Cleanup...'
            deleteDir()
            emailext subject: '$JOB_NAME Build Process',
                    attachLog: true,
                    body: '$BUILD_NUMBER | $BUILD_STATUS',
                    recipientProviders: [developers()],
                    mimeType: 'text/html'
        }
        success {
            echo 'Success'
            updateGitlabCommitStatus name: 'Build', state: 'success'
        }

        failure {
            echo 'Failure'
            updateGitlabCommitStatus name: 'Build', state: 'failed'
        }
    }
}