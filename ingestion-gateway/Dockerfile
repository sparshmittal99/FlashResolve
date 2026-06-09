# ==========================================
# Stage 1: Build the Spring Boot Application
# ==========================================
FROM maven:3.9-eclipse-temurin-25 AS builder
WORKDIR /app

# Copy the pom.xml and source code
COPY pom.xml .
COPY src ./src

# Package the application (skip tests to speed up cloud deployment)
RUN mvn clean package -DskipTests

# ==========================================
# Stage 2: Run the Application
# ==========================================
FROM eclipse-temurin:25-jre
WORKDIR /app

# Copy the compiled .jar file from the builder stage
COPY --from=builder /app/target/*.jar app.jar

# Expose the default port (Render will override this dynamically)
EXPOSE 8081

# Start the application
ENTRYPOINT ["java", "-jar", "app.jar"]