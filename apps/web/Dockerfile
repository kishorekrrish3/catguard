FROM node:20-alpine AS base
RUN npm install -g pnpm@9.11.0

WORKDIR /app

# Install dependencies
COPY package.json pnpm-workspace.yaml .npmrc ./
COPY apps/web/package.json apps/web/
RUN pnpm install --frozen-lockfile 2>/dev/null || pnpm install

# Copy source
COPY apps/web/ apps/web/

WORKDIR /app/apps/web

EXPOSE 3000
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "3000"]