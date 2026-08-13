FROM alpine:latest AS builder
RUN apk add --no-cache build-base cmake ninja
WORKDIR /app
COPY cxx-device-runtime/CMakeLists.txt ./
COPY cxx-device-runtime/include/ ./include/
COPY cxx-device-runtime/src/ ./src/
COPY cxx-device-runtime/proto/ ./proto/
RUN cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build build

FROM alpine:latest
RUN apk add --no-cache libstdc++ libgcc
WORKDIR /app
COPY --from=builder /app/build/qvalidate_device_runtime .
EXPOSE 50051
CMD ["./qvalidate_device_runtime"]
