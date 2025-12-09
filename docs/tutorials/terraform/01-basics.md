# Terraform Essentials

## Introduction
Terraform is an Infrastructure as Code (IaC) tool that lets you build, change, and version cloud and on-prem resources safely and efficiently.

## Core Concepts

### HCL Syntax
Terraform uses HashiCorp Configuration Language (HCL).
```hcl
resource "aws_instance" "app_server" {
  ami           = "ami-830c94e3"
  instance_type = "t2.micro"
}
```

### State Management
Terraform stores the state of your infrastructure in a local file (`terraform.tfstate`) or remotely (S3, Terraform Cloud). This state maps real resources to your configuration.

### Providers
Plugins that interact with APIs (e.g., AWS, Azure, Google Cloud).
```hcl
provider "aws" {
  region = "us-west-2"
}
```

### Modules
Containers for multiple resources to be used together. Modules allow reusability.

## Basic Workflow
1. `terraform init`: Initialize directory.
2. `terraform plan`: Preview changes.
3. `terraform apply`: Create resources.
4. `terraform destroy`: Destroy resources.
