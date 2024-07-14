// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "python_script.generated.h"

UCLASS()
class MYPROJECT_API Apython_script : public AActor
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	Apython_script();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

};
