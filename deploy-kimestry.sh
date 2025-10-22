#!/bin/bash

# Script to deploy Kimestry application using Helm

echo "Deploying Kimestry application..."

# NOTE: Make sure your external PostgreSQL database is accessible before deploying.
echo "Note: Ensure your external PostgreSQL database is accessible before continuing."

# Install the Kimestry chart
echo "Installing Kimestry chart..."
helm install kimestry ./kimestry-chart --create-namespace --namespace kimestry

echo "Kimestry has been deployed!"
echo ""
echo "To check the status of your deployment:"
echo "  kubectl get pods -n kimestry"
echo ""
echo "To check the services:"
echo "  kubectl get svc -n kimestry"
echo ""
echo "To view logs:"
echo "  kubectl logs -l app.kubernetes.io/name=kimestry-backend -n kimestry"
echo "  kubectl logs -l app.kubernetes.io/name=kimestry-frontend -n kimestry"
echo ""
echo "To access the application, find the external IP of the frontend service:"
echo "  kubectl get svc kimestry-frontend -n kimestry"
echo ""
echo "Important: Make sure your database configuration in values.yaml is correct:"
echo "  - Database host is reachable from the cluster"
echo "  - Database credentials are correct"
echo "  - Database name 'kimestry' exists"