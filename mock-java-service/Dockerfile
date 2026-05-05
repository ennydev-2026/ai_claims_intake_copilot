FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY pom.xml /workspace/pom.xml
COPY src /workspace/src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /workspace/target/mock-java-service-0.0.1-SNAPSHOT.jar /app/mock-java-service.jar
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "/app/mock-java-service.jar"]
