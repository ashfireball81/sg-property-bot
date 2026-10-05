FROM node:18-alpine as builder

WORKDIR /app

COPY api/package*.json ./
RUN npm install

COPY api/src ./src
COPY api/tsconfig.json ./
COPY api/prisma ./prisma

RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

COPY api/package*.json ./
RUN npm install --production

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/prisma ./prisma

RUN mkdir -p logs

EXPOSE 3000

CMD ["node", "dist/server.js"]
