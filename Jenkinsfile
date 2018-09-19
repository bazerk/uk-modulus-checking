/* *******************************************
Pypi repository configuration
**********************************************/
// PYPI configuration
def pypi_map = ['master': 'production', 'staging': 'staging', 'production': 'production', 'testing': 'testing']
def PYPI_REPO = (env.BRANCH_NAME in pypi_map) ? pypi_map[env.BRANCH_NAME] : 'staging'
def PYPI_URL = "https://pypi.holvi.net/holvi/${PYPI_REPO}"


pipeline {
    agent {
        node {
            label 'master'
        }
    }

    stages {
        stage('Prepare') {
            steps {
                sh 'python --version'
                sh 'virtualenv --version'

                sh """
                    virtualenv .env
                    . .env/bin/activate

                    python --version
                    pip --version

                    python setup.py build && python setup.py install
                """
            }
        }
        stage('Test') {
            steps {
                sh """
                    . .env/bin/activate
                    pip install -r ukmodulus/requirements-test.txt -i ${PYPI_URL}
                    coverage run ukmodulus/tests.py
                    coverage report
                    coverage xml
                """
            }
            post {
                always {
                    junit('results.xml')
                    cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
                }
            }
        }
        stage('Package') {
            when {
                anyOf {
                    branch 'testing'
                    branch 'master'
                }
            }
            steps {
                script {
                    build job: 'Packages/master', parameters: [
                        string(name: 'package_name', value: 'uk-modulus-checking'),
                        string(name: 'python_version', value: 'python'),
                        string(name: 'environment', value: 'testing'),
                        string(name: 'refspec', value: "${env.BRANCH_NAME}")
                    ], propagate: false, wait: false
                    build job: 'Packages/master', parameters: [
                        string(name: 'package_name', value: 'uk-modulus-checking'),
                        string(name: 'python_version', value: 'python'),
                        string(name: 'environment', value: 'staging'),
                        string(name: 'refspec', value: "${env.BRANCH_NAME}")
                    ], propagate: false, wait: false
                    build job: 'Packages/master', parameters: [
                        string(name: 'package_name', value: 'uk-modulus-checking'),
                        string(name: 'python_version', value: 'python'),
                        string(name: 'environment', value: 'production'),
                        string(name: 'refspec', value: "${env.BRANCH_NAME}")
                    ], propagate: false, wait: false
                }
            }
        }
    }
    post {
        always {
            deleteDir()
        }
    }
}
