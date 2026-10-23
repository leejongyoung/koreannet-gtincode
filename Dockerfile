# syntax=docker/dockerfile:1
FROM python:3.13-slim AS build
WORKDIR /src
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir build && python -m build --wheel --outdir /dist

FROM python:3.13-slim
LABEL org.opencontainers.image.title="koreannet-gtin" \
      org.opencontainers.image.description="Korean GTIN (barcode) lookup on Koreannet: CLI and browser UI" \
      org.opencontainers.image.source="https://github.com/leejongyoung/koreannet-gtincode" \
      org.opencontainers.image.licenses="MIT"
ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY --from=build /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl \
    && useradd --system --create-home --shell /usr/sbin/nologin app
USER app
EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8765/', timeout=3)"]
# 인자 없이 실행하면 브라우저 화면 서버, 인자를 주면 CLI: docker run --rm <image> 8801045759296
ENTRYPOINT ["koreannet-gtin"]
CMD ["web", "--host", "0.0.0.0", "--port", "8765", "--no-browser"]
