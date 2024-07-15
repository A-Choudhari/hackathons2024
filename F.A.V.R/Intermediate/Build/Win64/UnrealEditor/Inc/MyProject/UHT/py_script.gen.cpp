// Copyright Epic Games, Inc. All Rights Reserved.
/*===========================================================================
	Generated code exported from UnrealHeaderTool.
	DO NOT modify this manually! Edit the corresponding .h files instead!
===========================================================================*/

#include "UObject/GeneratedCppIncludes.h"
#include "MyProject/Public/py_script.h"
PRAGMA_DISABLE_DEPRECATION_WARNINGS
void EmptyLinkFunctionForGeneratedCodepy_script() {}
// Cross Module References
	ENGINE_API UClass* Z_Construct_UClass_AActor();
	MYPROJECT_API UClass* Z_Construct_UClass_Apy_script();
	MYPROJECT_API UClass* Z_Construct_UClass_Apy_script_NoRegister();
	UPackage* Z_Construct_UPackage__Script_MyProject();
// End Cross Module References
	void Apy_script::StaticRegisterNativesApy_script()
	{
	}
	IMPLEMENT_CLASS_NO_AUTO_REGISTRATION(Apy_script);
	UClass* Z_Construct_UClass_Apy_script_NoRegister()
	{
		return Apy_script::StaticClass();
	}
	struct Z_Construct_UClass_Apy_script_Statics
	{
		static UObject* (*const DependentSingletons[])();
#if WITH_METADATA
		static const UECodeGen_Private::FMetaDataPairParam Class_MetaDataParams[];
#endif
		static const FCppClassTypeInfoStatic StaticCppClassTypeInfo;
		static const UECodeGen_Private::FClassParams ClassParams;
	};
	UObject* (*const Z_Construct_UClass_Apy_script_Statics::DependentSingletons[])() = {
		(UObject* (*)())Z_Construct_UClass_AActor,
		(UObject* (*)())Z_Construct_UPackage__Script_MyProject,
	};
#if WITH_METADATA
	const UECodeGen_Private::FMetaDataPairParam Z_Construct_UClass_Apy_script_Statics::Class_MetaDataParams[] = {
		{ "IncludePath", "py_script.h" },
		{ "ModuleRelativePath", "Public/py_script.h" },
	};
#endif
	const FCppClassTypeInfoStatic Z_Construct_UClass_Apy_script_Statics::StaticCppClassTypeInfo = {
		TCppClassTypeTraits<Apy_script>::IsAbstract,
	};
	const UECodeGen_Private::FClassParams Z_Construct_UClass_Apy_script_Statics::ClassParams = {
		&Apy_script::StaticClass,
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
		METADATA_PARAMS(Z_Construct_UClass_Apy_script_Statics::Class_MetaDataParams, UE_ARRAY_COUNT(Z_Construct_UClass_Apy_script_Statics::Class_MetaDataParams))
	};
	UClass* Z_Construct_UClass_Apy_script()
	{
		if (!Z_Registration_Info_UClass_Apy_script.OuterSingleton)
		{
			UECodeGen_Private::ConstructUClass(Z_Registration_Info_UClass_Apy_script.OuterSingleton, Z_Construct_UClass_Apy_script_Statics::ClassParams);
		}
		return Z_Registration_Info_UClass_Apy_script.OuterSingleton;
	}
	template<> MYPROJECT_API UClass* StaticClass<Apy_script>()
	{
		return Apy_script::StaticClass();
	}
	DEFINE_VTABLE_PTR_HELPER_CTOR(Apy_script);
	Apy_script::~Apy_script() {}
	struct Z_CompiledInDeferFile_FID_Users_prith_zwg29uj_OneDrive_Documents_Unreal_Projects_MyProject_Source_MyProject_Public_py_script_h_Statics
	{
		static const FClassRegisterCompiledInInfo ClassInfo[];
	};
	const FClassRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Users_prith_zwg29uj_OneDrive_Documents_Unreal_Projects_MyProject_Source_MyProject_Public_py_script_h_Statics::ClassInfo[] = {
		{ Z_Construct_UClass_Apy_script, Apy_script::StaticClass, TEXT("Apy_script"), &Z_Registration_Info_UClass_Apy_script, CONSTRUCT_RELOAD_VERSION_INFO(FClassReloadVersionInfo, sizeof(Apy_script), 450944108U) },
	};
	static FRegisterCompiledInInfo Z_CompiledInDeferFile_FID_Users_prith_zwg29uj_OneDrive_Documents_Unreal_Projects_MyProject_Source_MyProject_Public_py_script_h_2701467991(TEXT("/Script/MyProject"),
		Z_CompiledInDeferFile_FID_Users_prith_zwg29uj_OneDrive_Documents_Unreal_Projects_MyProject_Source_MyProject_Public_py_script_h_Statics::ClassInfo, UE_ARRAY_COUNT(Z_CompiledInDeferFile_FID_Users_prith_zwg29uj_OneDrive_Documents_Unreal_Projects_MyProject_Source_MyProject_Public_py_script_h_Statics::ClassInfo),
		nullptr, 0,
		nullptr, 0);
PRAGMA_ENABLE_DEPRECATION_WARNINGS
