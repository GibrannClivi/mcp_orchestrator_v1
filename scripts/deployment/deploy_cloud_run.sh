#!/bin/bash
# Deploy Orchestrator to Google Cloud Run
PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
REGION=${GOOGLE_CLOUD_RUN_REGION:-us-central1}
SERVICE_NAME=mcp-orchestrator
IMAGE=gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

gcloud builds submit --tag $IMAGE

gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated
