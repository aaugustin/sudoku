FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY sudoku .
RUN go build ./cmd/sudoku

FROM scratch AS runner
WORKDIR /app
COPY --from=builder /app/sudoku /app/sudoku
CMD ["./sudoku", "serve", "-host", "0.0.0.0", "-port", "8080"]
EXPOSE 8080
