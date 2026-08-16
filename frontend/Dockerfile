# syntax=docker/dockerfile:1

FROM node:20-alpine AS base
WORKDIR /app
RUN corepack enable

FROM base AS deps
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build
# Next.js output file tracing has a known issue under pnpm where nested,
# per-package "@swc/helpers" copies (e.g. under node_modules/.pnpm/next@.../)
# only get their CJS files traced, missing the ESM variant Next's
# require-hook needs at runtime. Replace every traced copy (whether a
# symlink or an incomplete real directory) with the full, fully-installed
# package, skipping the canonical copy itself.
RUN src="$(readlink -f node_modules/@swc/helpers)" && \
    find .next/standalone -path "*/node_modules/@swc/helpers" | while read -r dir; do \
      real="$(readlink -f "$dir" || true)"; \
      if [ "$real" != "$src" ]; then rm -rf "$dir" && cp -RL "$src" "$dir"; fi; \
    done

FROM base AS runner
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
