$GITHUB_USERNAME = "VeronikaShevchuk"
$IMAGE_PREFIX = "ghcr.io/$GITHUB_USERNAME/architecture-cinemaabyss-main"
$CR_PAT = "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"

Write-Host "=== Building and Pushing Docker Images to GitHub Container Registry ===" -ForegroundColor Green

Write-Host "`n1. Logging into GitHub Container Registry..." -ForegroundColor Yellow
$loginResult = echo $CR_PAT | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin
if ($LASTEXITCODE -ne 0) {
    Write-Host " Failed to login to GitHub Container Registry" -ForegroundColor Red
    exit 1
}
Write-Host " Successfully logged in" -ForegroundColor Green

$services = @(
    "monolith",
    "movies-service", 
    "events-service",
    "proxy-service"
)

foreach ($service in $services) {
    Write-Host "`n2. Building $service..." -ForegroundColor Cyan
    
    # Проверяем что папка существует
    $servicePath = "./src/microservices/$service"
    if (-not (Test-Path $servicePath)) {
        Write-Host " Directory $servicePath does not exist" -ForegroundColor Red
        continue
    }
    
    # Собираем образ
    Write-Host "   Building image: $IMAGE_PREFIX/$service`:latest"
    docker build -t "$IMAGE_PREFIX/$service`:latest" $servicePath
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host " Failed to build $service" -ForegroundColor Red
        continue
    }
    
    Write-Host " Successfully built $service" -ForegroundColor Green
    
    # Пушим образ
    Write-Host "3. Pushing $service..." -ForegroundColor Cyan
    docker push "$IMAGE_PREFIX/$service`:latest"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host " Failed to push $service" -ForegroundColor Red
        continue
    }
    
    Write-Host " Successfully pushed $service" -ForegroundColor Green
}

Write-Host "`n=== All images processed! ===" -ForegroundColor Green
Write-Host "Check your packages at: https://github.com/VeronikaShevchuk?tab=packages" -ForegroundColor Yellow
