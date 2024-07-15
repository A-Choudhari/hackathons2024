// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "MyProject/python_script.h"
PRAGMA_DISABLE_DEPRECATION_WARNINGS
void EmptyLinkFunctionForGeneratedCodepython_script() {}
// Cross Module References
	ENGINE_API UClass* Z_Construct_UClass_AActor();
	MYPROJECT_API UClass* Z_Construct_UClass_Apython_script();
	MYPROJECT_API UClass* Z_Construct_UClass_Apython_script_NoRegister();
	UPackage* Z_Construct_UPackage__Script_MyProject();
// End Cross Module References
	void Apython_script::StaticRegisterNativesApython_script()
	{
	}
	IMPLEMENT_CLASS_NO_AUTO_REGISTRATION(Apython_script);
	UClass* Z_Construct_UClass_Apython_script_NoRegister()
	{
		return Apython_script::StaticClass();
	}
	struct Z_Construct_UClass_Apython_script_Statics
	{
		static UObject* (*const DependentSingletons[])();
#if WITH_METADATA
		static const UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[];
#endif
		static const FCppClassTypeInfoStatic StaticCppClassTypeInfo;
		static const UECodeGen_Private::FClassParams ClassParams;
	};
	UObject* (*const Z_Construct_UClass_Apython_script_Statics::DependentSingletons[])() = {
		(UObject* (*)())Z_Construct_UClass_AActor,
		(UObject* (*)())Z_Construct_UPackage__Script_MyProject,
	};
#if WITH_METADATA
	const UECodeGen_Private::FMetaDataPairParam Z_Construct_UClass_Apython_script_Statics::Class_MetaDataParams[] = {
		{ "IncludePath", "python_script.h" },
		{ "ModuleRelativePath", "python_script.h" },
	};
#endif
	const FCppClassTypeInfoStatic Z_Construct_UClass_Apython_script_Statics::StaticCppClassTypeInfo = {
		TCppClassTypeTraits<Apython_script>::IsAbstract,
	};
	const UECodeGen_Private::FClassParams Z_Construct_UClass_Apython_script_Statics::ClassParams = {
		&Apython_script::StaticClass,
		"Engine",
		&StaticCppClassTypeInfo,
		DependentSingletons,
		nullptr,
		nullptr,
		nullptr,
		UE_ARRAY_COUNT(DependentSingletons),
		0,
		0,
		0,
		0x009000A4u,
		METADATA_PARAMS(Z_Construct_UClass_Apython_script_Statics::Class_MetaDataParams, UE_ARRAY_COUNT(Z_Construct_UClass_Apython_script_Statics::Class_MetaDataParams))
	};
	UClass* Z_Construct_UClass_Apython_script()
	{
		if (!Z_Registration_Info_UClass_Apython_script.OuterSingleton)
		{
			UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_Apython_script.OuterSingleton, Z_Construct_UClass_Apython_script_Statics::ClassParams);
		}
		return Z_Registration_Info_UClass_Apython_script.OuterSingleton;
	}
	template<> MYPROJECT_API UClass* StaticClass<Apython_script>()
	{
		return Apython_script::StaticClass();
	}
	DEFINE_VTABLE_PTR_HELPER_CTOR(Apython_script);
	Apython_script::~Apython_script() {}
	struct Z_CompiledInDeferFile_FID_Users_prith_zwg29uj_OneDrive_Documents_Unreal_Projects_MyProject_Source_MyProject_python_script_h_Statics
	{
		static const FClassRegisterCompiledInInfo ClassInfo[];
	};
	const FClassRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Users_prith_zwg29uj_OneDrive_Documents_Unreal_Projects_MyProject_Source_MyProject_python_script_h_Statics::ClassInfo[] = {
		{ Z_Construct_UClass_Apython_script, Apython_script::StaticClass, TEXT("Apython_script"), &Z_Registration_Info_UClass_Apython_script, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(Apython_script), 3842953471U) },
	};
	static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Users_prith_zwg29uj_OneDrive_Documents_Unreal_Projects_MyProject_Source_MyProject_python_script_h_1477193521(TEXT("/Script/MyProject"),
		Z_CompiledInDeferFile_FID_Users_prith_zwg29uj_OneDrive_Documents_Unreal_Projects_MyProject_Source_MyProject_python_script_h_Statics::ClassInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Users_prith_zwg29uj_OneDrive_Documents_Unreal_Projects_MyProject_Source_MyProject_python_script_h_Statics::ClassInfo),
		nullptr, 0,
		nullptr, 0);
PRAGMA_ENABLE_DEPRECATION_WARNINGS
