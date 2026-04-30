# Build stage — compila o frontend com bun
FROM oven/bun:1-alpine AS builder

WORKDIR /app

COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

COPY . .
RUN bun run build

# Runtime stage — nginx serve os assets estáticos
FROM nginx:alpine AS runtime

# TanStack Start com Cloudflare adapter produz assets em dist/client/
# Se o seu build gerar dist/ diretamente, ajuste o caminho abaixo
COPY --from=builder /app/dist/client /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
