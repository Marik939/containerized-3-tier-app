# Containerized 3-Tier Web Application

## 1. Project Overview

This project is a containerized 3-tier web application with a frontend, backend and MySQL database.

The application was first developed and tested locally using Docker Compose. After that, it was deployed to OpenShift/Rahti.

The application allows the user to view data from MySQL and increase a page view counter through the frontend.

### Technologies used

- Nginx - frontend web server and reverse proxy
- Flask - backend REST API
- MySQL 8.4 - database
- Docker - containerization
- Docker Compose - local deployment
- Docker Hub - container image registry
- OpenShift / Rahti - cloud deployment
- PersistentVolumeClaim (PVC) - persistent database storage
- ConfigMap - application configuration
- Secret - database passwords


## 2. Architecture

The application consists of three main layers:

```text
                    Internet
                       |
                       v
              OpenShift Route
                       |
                       v
              +----------------+
              |    Frontend    |
              |     Nginx      |
              +-------+--------+
                      |
                    /api
                      |
                      v
              +----------------+
              |    Backend     |
              | Flask / Python |
              +-------+--------+
                      |
                      v
              +----------------+
              |    MySQL DB    |
              |   Persistent   |
              |    storage     |
              +----------------+

The frontend is the only part exposed to the Internet.
The backend and database use internal OpenShift Services and are not directly exposed outside the cluster.
```

  ## 3. Project Structure

containerized-3-tier-app/
│
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── db/
│   └── init/
│       └── init.sql
│
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   └── nginx.conf
│
├── rahti/
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── configmap.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── frontend-route.yaml
│   ├── mysql-deployment.yaml
│   ├── mysql-pvc.yaml
│   ├── mysql-service.yaml
│   └── secret.yaml
│
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-compose.yml
└── README.md

Main directories
backend/ contains the Flask application and backend Dockerfile.

frontend/ contains the Nginx configuration and frontend page.

db/ contains the initial MySQL database setup.

rahti/ contains the OpenShift deployment manifests.

docker-compose*.yml files are used for local Docker deployment.

## 4. Application Functionality

The frontend communicates with the Flask backend through the /api endpoint.

The backend reads the following information from MySQL:

MySQL server time
Current page view count

The application also has an Add visit button.

When the button is pressed, the frontend sends a POST request to /api/visit. The backend then increases the page_views counter in MySQL.

This was used to test both reading and writing data between the application and the database.

## 5. Local Docker Deployment
![Local application](screenshots/local-app.png)
The application was first tested locally using Docker Compose.

The development environment was started with:
docker compose -f docker-compose.dev.yml --env-file .env up --build -d

The application was available locally at:
http://localhost:8080

The local test confirmed that:

Nginx served the frontend.
Flask handled the API requests.
Flask successfully connected to MySQL.
MySQL returned the server time and page view count.
The page view counter could be increased using the Add visit button.
Local application

## 6. Docker Images

The application images were built and pushed to Docker Hub.

Backend
maryna999/lemp-backend:1.0.0
maryna999/lemp-backend:1.0.1
maryna999/lemp-backend:1.0.2
Frontend
maryna999/lemp-frontend:1.0.0
maryna999/lemp-frontend:1.0.1
maryna999/lemp-frontend:1.0.2

Versioned image tags were used so that application updates could be tested between different versions.

## 7. OpenShift / Rahti Deployment

The application was deployed to the my-first-rahti-app OpenShift project.

The following resources were created:

Resource	Purpose
frontend Deployment	Runs the Nginx frontend
frontend Service	Provides internal access to the frontend
frontend Route	Exposes the frontend to the Internet
backend Deployment	Runs the Flask backend
backend Service	Provides internal access to the backend
db Deployment	Runs MySQL
db Service	Provides internal access to MySQL
mysql-pvc	Provides persistent storage for MySQL
app-config ConfigMap	Stores non-sensitive database configuration
mysql-secret Secret	Stores database passwords

The final application contained one frontend Pod, one backend Pod and one MySQL Pod.

The backend and database Services use ClusterIP and are only accessible inside the OpenShift cluster.

## 8. Configuration
ConfigMap
The ConfigMap contains non-sensitive database configuration:

DB_HOST=db
DB_USER=appuser
DB_NAME=appdb
Secret

Database passwords are stored in an OpenShift Secret instead of being included directly in the application configuration.

The actual secret values are not included in this repository.

## 9. Persistent Storage
MySQL uses a PersistentVolumeClaim named:
mysql-pvc
The PVC provides persistent storage for the MySQL data.
This means that database data should remain available even if the MySQL Pod is deleted and recreated.

## 10. Tests and Experiments

## 10.1 READ + WRITE Test
![READ and WRITE test](screenshots/read-write-test.png)
The application was tested through the frontend.

The frontend successfully received data from MySQL through the Flask backend. The MySQL server time and page_views value were displayed.

The Add visit button increased the page_views counter.

This confirmed that both reading and writing data through the application worked correctly.

## 10.2 Persistence Test
![MySQL Pod recovery](screenshots/pod-recovery.png)
The MySQL Pod was deleted manually to simulate Pod replacement.

OpenShift automatically created a new MySQL Pod. After the new Pod became Running, the application was tested again.

The page_views value remained 10.

This confirmed that the database data persisted through Pod replacement using the PersistentVolumeClaim.

## 10.3 Scaling Test
![Scaling test](screenshots/scale-test.png)
The backend Deployment was scaled from 1 to 2 replicas.

Both backend Pods reached the Running state and the application continued to work correctly.

The page_views value remained 10.

## 10.4 Application Update Test
![Application update test](screenshots/application-update.jpg)
The backend image was updated from version 1.0.1 to 1.0.2.

OpenShift performed a rolling update and replaced the old backend Pod with a new Pod running the updated image.

After the update, the application returned the new version message:

Hello from MySQL via Flask! v1.0.2

The page_views value remained 10, confirming that the application update did not affect the database data.

## 10.5 Pod Failure and Recovery Test
![Pod failure and recovery test](screenshots/pod-recovery.png)
One backend Pod was manually deleted to simulate a Pod failure.

The Deployment automatically created a replacement Pod, while the second backend Pod continued running.

After the replacement Pod became Running, the application was tested again and returned the expected response.

The page_views value remained 10.

This confirmed that the backend recovered automatically without database data loss.

## 10.6 Network / Access Test
![Network and access test](screenshots/network-test.jpg)
The OpenShift Services were checked after deployment.

The backend and database use internal ClusterIP Services and do not have external IP addresses.

The frontend is exposed through an OpenShift Route.

Therefore, only the frontend is directly accessible from the Internet, while the backend and database remain internal to the cluster.

## 11. Problems Encountered and Fixes
Nginx permission problem
The frontend Pod initially failed because Nginx tried to write temporary files to directories where the OpenShift container did not have permission.
The Nginx configuration was changed to use /tmp for temporary files and the PID file.
After rebuilding the frontend image, the Pod started successfully.

Missing MySQL table
The backend initially returned an HTTP 500 error because the page_views table did not exist in the already initialized MySQL data directory.
The table was created in the existing database without deleting the PersistentVolumeClaim.
After that, the backend was able to read and update the page view counter correctly.

Backend application update
The backend was initially running version 1.0.1.
The application message was changed and a new image version 1.0.2 was built and pushed to Docker Hub.
The OpenShift Deployment was then updated to use the new image.
The rolling update successfully replaced the old backend Pod.

## 12. Final Result
![Local application](screenshots/local-app.png)
The application was successfully deployed to Rahti/OpenShift.

The final architecture contains:

Nginx frontend
Flask backend
MySQL database
Internal Services for backend and database
OpenShift Route for the frontend
ConfigMap for configuration
Secret for database passwords
PersistentVolumeClaim for MySQL storage

The application was tested for:

READ and WRITE operations
Database persistence
Backend scaling
Application update
Pod failure and recovery
Network and access configuration
Application URL
https://frontend-my-first-rahti-app.2.rahtiapp.fi

The frontend is publicly accessible through the OpenShift Route, while the backend and database remain internal to the cluster.