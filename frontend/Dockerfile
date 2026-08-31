FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
# Next.js's standalone server.js passes this straight to Node's
# server.listen(port, hostname) -- it needs a bare hostname, not a URL.
# "0.0.0.0" binds on all interfaces inside the container, which is required
# for the port mapping in infra/docker-compose.yml to reach it; "http://localhost"
# here made Node's DNS lookup fail immediately (ENOTFOUND) since a URL with
# a scheme isn't a valid hostname.
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
