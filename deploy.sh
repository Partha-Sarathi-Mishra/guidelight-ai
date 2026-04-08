#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
# Guidelight AI – Google Cloud Run Deployment Script
# ──────────────────────────────────────────────────────────
set -euo pipefail

# ── Configuration ─────────────────────────────────────────
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-gcp-project-id}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE_NAME="guidelight-ai"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🔧 Project:  ${PROJECT_ID}"
echo "🌍 Region:   ${REGION}"
echo "🐳 Image:    ${IMAGE}"
echo ""

# ── Step 1: Set project ──────────────────────────────────
echo "▶ Setting active project..."
gcloud config set project "${PROJECT_ID}"

# ── Step 2: Build container image ────────────────────────
echo "▶ Building container image..."
gcloud builds submit --tag "${IMAGE}" .

# ── Step 3: Deploy to Cloud Run ──────────────────────────
echo "▶ Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE}" \
    --region "${REGION}" \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},GEMINI_MODEL=gemini-3.1-flash-lite-preview,GOOGLE_API_KEY=${GOOGLE_API_KEY:-}" \
    --min-instances 0 \
    --max-instances 3

echo ""
echo "✅ Deployment complete!"
echo "🌐 Service URL:"
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format "value(status.url)"
