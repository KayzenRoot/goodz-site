# Official Docker Hub python:3.12-slim multi-arch index (3.12.16-slim-trixie).
# Digest resolves linux/amd64 and linux/arm64; verified by tools/verify_base_image.sh.
FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && addgroup --system goodz && adduser --system --ingroup goodz goodz
COPY . .
RUN mkdir -p /app/data/uploads && chown -R goodz:goodz /app/data
USER goodz
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
