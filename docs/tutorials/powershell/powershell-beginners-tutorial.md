# PowerShell Beginner's Tutorial

This tutorial introduces PowerShell for complete beginners, covering basic concepts, scripting, and object-oriented programming. PowerShell is a powerful scripting language and shell for Windows, Linux, and macOS.

## Table of Contents
1. [What is PowerShell?](#what-is-powershell)
2. [Getting Started](#getting-started)
3. [Basic Concepts](#basic-concepts)
4. [Scripting Fundamentals](#scripting-fundamentals)
5. [Working with Objects](#working-with-objects)
6. [Object-Oriented Programming in PowerShell](#object-oriented-programming-in-powershell)
7. [Best Practices](#best-practices)
8. [Next Steps](#next-steps)

## What is PowerShell?

PowerShell is a task automation and configuration management framework from Microsoft. It consists of:
- A command-line shell
- A scripting language
- A framework for processing cmdlets (pronounced "command-lets")

PowerShell is built on .NET and works with objects rather than text, making it powerful for automation.

## Getting Started

### Installation
- **Windows**: PowerShell is pre-installed (Windows PowerShell 5.1). For newer versions, install PowerShell Core from [microsoft.com/powershell](https://microsoft.com/powershell)
- **Linux/macOS**: Install PowerShell Core using package managers

### Opening PowerShell
- Windows: Search for "PowerShell" or "pwsh" (for PowerShell Core)
- Linux/macOS: Open terminal and type `pwsh`

### First Commands
```powershell
# Display version
$PSVersionTable.PSVersion

# Get help
Get-Help

# List commands
Get-Command
```

## Basic Concepts

### Cmdlets
Cmdlets are lightweight commands that perform specific functions. They follow Verb-Noun naming convention.

```powershell
# Get processes
Get-Process

# Get services
Get-Service

# Stop a service
Stop-Service -Name "spooler"
```

### Pipeline
The pipeline (`|`) passes output from one cmdlet to another.

```powershell
# Get running processes and sort by CPU usage
Get-Process | Sort-Object -Property CPU -Descending | Select-Object -First 5
```

### Variables
Variables start with `$` and can hold any type of object.

```powershell
# String variable
$name = "John"

# Integer
$age = 25

# Array
$numbers = 1, 2, 3, 4, 5

# Hash table
$person = @{
    Name = "John"
    Age = 25
    City = "New York"
}
```

### Data Types
PowerShell automatically determines data types, but you can specify them:

```powershell
[string]$name = "Alice"
[int]$count = 10
[datetime]$date = Get-Date
[bool]$isActive = $true
```

## Scripting Fundamentals

### Creating Scripts
Save commands in `.ps1` files.

```powershell
# hello.ps1
Write-Host "Hello, PowerShell!"
$name = Read-Host "What's your name?"
Write-Host "Nice to meet you, $name!"
```

Run scripts:
```powershell
# From PowerShell
.\hello.ps1

# Or specify full path
& "C:\Scripts\hello.ps1"
```

### Control Structures

#### If-Else
```powershell
$number = 10

if ($number -gt 5) {
    Write-Host "Number is greater than 5"
} elseif ($number -eq 5) {
    Write-Host "Number equals 5"
} else {
    Write-Host "Number is less than 5"
}
```

#### Loops
```powershell
# For loop
for ($i = 1; $i -le 5; $i++) {
    Write-Host "Count: $i"
}

# Foreach loop
$fruits = "Apple", "Banana", "Orange"
foreach ($fruit in $fruits) {
    Write-Host "I like $fruit"
}

# While loop
$count = 1
while ($count -le 3) {
    Write-Host "While loop iteration: $count"
    $count++
}
```

### Functions
Functions encapsulate reusable code.

```powershell
function Get-Greeting {
    param(
        [string]$Name,
        [string]$TimeOfDay = "day"
    )

    "Good $TimeOfDay, $Name!"
}

# Call the function
Get-Greeting -Name "Alice" -TimeOfDay "morning"
Get-Greeting "Bob"  # Positional parameters
```

## Working with Objects

PowerShell works with objects, not just text. Every cmdlet returns objects with properties and methods.

```powershell
# Get a process object
$process = Get-Process -Name "notepad"

# Access properties
$process.Name
$process.Id
$process.CPU

# Get all properties
$process | Get-Member

# Use methods
$process.Kill()
```

### Filtering and Selecting
```powershell
# Filter objects
Get-Process | Where-Object { $_.CPU -gt 10 }

# Select specific properties
Get-Service | Select-Object -Property Name, Status, DisplayName

# Format output
Get-Process | Format-Table -Property Name, CPU, Memory -AutoSize
```

## Object-Oriented Programming in PowerShell

PowerShell 5.0+ supports classes and object-oriented programming.

### Defining Classes
```powershell
class Person {
    # Properties
    [string]$Name
    [int]$Age
    [string]$City

    # Constructor
    Person([string]$name, [int]$age) {
        $this.Name = $name
        $this.Age = $age
        $this.City = "Unknown"
    }

    # Method
    [string] GetInfo() {
        return "$($this.Name) is $($this.Age) years old and lives in $($this.City)."
    }

    # Static method
    static [string] GetSpecies() {
        return "Human"
    }
}
```

### Creating Objects
```powershell
# Create an instance
$person1 = [Person]::new("Alice", 30)
$person1.City = "New York"

# Call method
$person1.GetInfo()

# Call static method
[Person]::GetSpecies()
```

### Inheritance
```powershell
class Employee : Person {
    [string]$Department
    [decimal]$Salary

    Employee([string]$name, [int]$age, [string]$dept) : base($name, $age) {
        $this.Department = $dept
        $this.Salary = 50000
    }

    [string] GetEmployeeInfo() {
        return "$($this.GetInfo()) Works in $($this.Department) department."
    }
}

# Create employee
$emp = [Employee]::new("Bob", 35, "IT")
$emp.GetEmployeeInfo()
```

### Advanced OOP Concepts

#### Properties with Getters/Setters
```powershell
class Temperature {
    hidden [double]$_celsius

    [double]$Celsius {
        get { return $this._celsius }
        set {
            if ($value -lt -273.15) {
                throw "Temperature cannot be below absolute zero"
            }
            $this._celsius = $value
        }
    }

    [double]$Fahrenheit {
        get { return ($this._celsius * 9/5) + 32 }
        set { $this.Celsius = ($value - 32) * 5/9 }
    }
}

$temp = [Temperature]::new()
$temp.Celsius = 25
Write-Host "Celsius: $($temp.Celsius), Fahrenheit: $($temp.Fahrenheit)"
```

#### Interfaces (using abstract classes)
```powershell
class IShape {
    [double] GetArea() {
        throw "Not implemented"
    }
}

class Circle : IShape {
    [double]$Radius

    Circle([double]$radius) {
        $this.Radius = $radius
    }

    [double] GetArea() {
        return [Math]::PI * $this.Radius * $this.Radius
    }
}

$circle = [Circle]::new(5)
$circle.GetArea()
```

## Best Practices

1. **Use Proper Naming**: Follow Verb-Noun for cmdlets and functions
2. **Handle Errors**: Use `try/catch` for error handling
3. **Comment Your Code**: Use `#` for comments
4. **Use Parameters**: Make functions flexible with parameters
5. **Test Your Scripts**: Use Pester for testing
6. **Follow PowerShell Style**: Use PSScriptAnalyzer for linting

### Error Handling
```powershell
try {
    $result = Get-Content -Path "nonexistent.txt" -ErrorAction Stop
} catch {
    Write-Warning "File not found: $($_.Exception.Message)"
} finally {
    Write-Host "Cleanup code here"
}
```

### Advanced Functions
```powershell
function Get-SystemInfo {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ComputerName,

        [Parameter()]
        [switch]$IncludeDiskSpace
    )

    begin {
        Write-Verbose "Starting Get-SystemInfo for $ComputerName"
    }

    process {
        $os = Get-WmiObject -Class Win32_OperatingSystem -ComputerName $ComputerName
        $result = [PSCustomObject]@{
            ComputerName = $ComputerName
            OS = $os.Caption
            Version = $os.Version
        }

        if ($IncludeDiskSpace) {
            $disks = Get-WmiObject -Class Win32_LogicalDisk -ComputerName $ComputerName -Filter "DriveType=3"
            $result | Add-Member -MemberType NoteProperty -Name "DiskSpace" -Value $disks
        }

        $result
    }

    end {
        Write-Verbose "Completed Get-SystemInfo"
    }
}
```

## Next Steps

1. **Practice**: Try the examples in this tutorial
2. **Explore Cmdlets**: Use `Get-Command` to discover more cmdlets
3. **Learn Modules**: Study how to create and use PowerShell modules
4. **Automation**: Look into PowerShell DSC for configuration management
5. **Resources**:
   - [Microsoft PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)
   - [PowerShell Gallery](https://www.powershellgallery.com/)
   - [PowerShell.org](https://powershell.org/)

Remember, PowerShell is powerful because it works with objects. Embrace the object-oriented nature and you'll unlock its full potential!
