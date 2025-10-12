# NuGet Packaging Tutorial for PowerShell Modules

This tutorial explains how to compile and package your GDS PowerShell modules into NuGet packages for distribution and deployment.

## Prerequisites

1. **NuGet CLI**: Install NuGet CLI (nuget.exe) or use dotnet CLI.
   - On Windows: Download from nuget.org
   - On Linux/macOS: Use `dotnet nuget` commands

2. **PowerShell Module Manifests**: Each module must have a valid `.psd1` manifest file.

3. **Module Structure**: Ensure modules are in `powershell/modules/` with proper structure.

## Step 1: Create a Nuspec File for Each Module

A `.nuspec` file describes the NuGet package metadata. Create one for each module.

Example for `GDS.MSSQL.Build`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
  <metadata>
    <id>GDS.MSSQL.Build</id>
    <version>1.0.0</version>
    <authors>Your Name</authors>
    <owners>Your Organization</owners>
    <description>PowerShell module for SQL Server build operations</description>
    <tags>powershell sql-server build gds</tags>
    <dependencies>
      <dependency id="GDS.MSSQL.Core" version="1.0.0" />
    </dependencies>
  </metadata>
  <files>
    <file src="**\*.*" target="tools" />
  </files>
</package>
```

Save this as `GDS.MSSQL.Build.nuspec` in the module's root directory.

## Step 2: Build the NuGet Package

### Using NuGet CLI

```bash
# Navigate to the module directory
cd powershell/modules/GDS.MSSQL.Build

# Pack the module
nuget pack GDS.MSSQL.Build.nuspec -OutputDirectory ../../../build/packages
```

### Using dotnet CLI

```bash
# Pack the module
dotnet nuget pack powershell/modules/GDS.MSSQL.Build/GDS.MSSQL.Build.nuspec --output build/packages
```

## Step 3: Automated Build Script

Use the provided `build/build.ps1` script to build all modules:

```powershell
# Run from the project root
.\powershell\build\build.ps1 -PackageNuGet $true
```

The script will:
1. Copy modules to build directory
2. Generate .nuspec files if missing
3. Create .nupkg files for each module

## Step 4: Publish to NuGet Feed

### To PowerShell Gallery

```powershell
# Get API key from https://www.powershellgallery.com/account
$apiKey = "your-api-key"

# Publish each package
Publish-Module -Path .\build\packages\GDS.MSSQL.Build.1.0.0.nupkg -NuGetApiKey $apiKey
```

### To Private NuGet Feed

```powershell
# For Azure DevOps or private feed
Publish-Module -Path .\build\packages\GDS.MSSQL.Build.1.0.0.nupkg -Repository "MyPrivateFeed" -NuGetApiKey $apiKey
```

## Step 5: Install from NuGet Package

Users can install your modules from the package:

```powershell
# Install from PowerShell Gallery
Install-Module -Name GDS.MSSQL.Build

# Or from local package
Install-Package -Source .\build\packages -Name GDS.MSSQL.Build
```

## Best Practices

1. **Versioning**: Use semantic versioning (e.g., 1.0.0, 1.1.0, 2.0.0)
2. **Dependencies**: Declare module dependencies in .nuspec
3. **Testing**: Test packages locally before publishing
4. **Signing**: Consider code signing for production modules
5. **CI/CD**: Integrate packaging into your build pipeline

## Troubleshooting

- **Missing Dependencies**: Ensure all required modules are packaged and available
- **Version Conflicts**: Check version numbers in manifests and nuspec
- **Permissions**: Ensure write access to output directories

For more details, see the Microsoft documentation on [PowerShell Module Packaging](https://docs.microsoft.com/en-us/powershell/scripting/gallery/how-to/publishing-packages/publish-to-powershell-gallery).
