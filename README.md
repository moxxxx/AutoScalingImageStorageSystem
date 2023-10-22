# AutoScalingImageStorageSystem

The Elastic Image Storage System is a scalable and efficient image storage and management solution that leverages various Flask components and AWS services. This README file provides an overview of the system, its components, and how to set it up.

## Table of Contents

1. [Introduction](#introduction)
2. [Components](#components)
    - [Flask Components](#flask-components)
    - [AWS Services](#aws-services)
3. [System Architecture](#system-architecture)
4. [Getting Started](#getting-started)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Monitoring and Scaling](#monitoring-and-scaling)

## 1. Introduction

The Auto Scaling Image Storage System is designed to provide a scalable and reliable solution for storing and managing images. It consists of Flask components hosted on AWS EC2 instances and utilizes various AWS services including S3, RDS, CloudWatch for different aspects of the system.

## 2. Components

### Flask Components

1. **Web GUI Flask App**: This component provides a user-friendly web interface for uploading, managing, and retrieving images.

2. **Manager UI Flask App**: The Manager UI allows administrators to configure the system, monitor its performance, and manage user accounts.

3. **Image Storage Flask App**: Responsible for the storage and retrieval of images, as well as handling image metadata.

4. **Autoscaler Flask App**: The Autoscaler component dynamically adjusts the number of Memcache Flask Apps based on system load.

5. **Memcache Flask Apps (8 instances)**: These apps work together to cache frequently accessed data, improving system performance.

### AWS Services

1. **EC2 Instances**: The Flask components are hosted on AWS EC2 instances, providing scalable and reliable computing resources.

2. **RDS (Relational Database Service)**: RDS is used to store keys and image paths, facilitating efficient retrieval and management of image metadata.

3. **S3 (Simple Storage Service)**: S3 is used to store the actual image files, ensuring durability and availability.

4. **CloudWatch**: CloudWatch is employed for monitoring system statistics, particularly for the Memcache Flask Apps, enabling proactive performance management.

## 3. System Architecture

The Elastic Image Storage System architecture leverages the Flask components for user interaction and image management, AWS EC2 instances for hosting these components, RDS for database storage, S3 for image storage, and CloudWatch for monitoring system health. The Autoscaler Flask App ensures the system dynamically adapts to varying workloads by managing the number of Memcache Flask Apps.

![System Architecture](architecture-diagram.png)

## 4. Getting Started

Before deploying the system, make sure you have the necessary AWS credentials and resources set up. Clone this repository to your EC2 instances and follow the installation and configuration steps outlined in the individual Flask component README files.

## 5. Configuration

Each Flask component and AWS service may require specific configuration. Edit run_main.sh to modify RDE setting.

## 6. Usage

The system is designed for storing and managing images. Users can access the Web GUI to upload, retrieve, and manage images, while administrators can use the Manager UI to configure and monitor the system.

Detailed usage instructions can be found in the README files for each Flask component.

## 7. Monitoring and Scaling

CloudWatch is used for monitoring the health and performance of the Memcache Flask Apps. The Autoscaler Flask App ensures that the system scales dynamically to handle varying workloads.
