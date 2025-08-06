function Get-RegistrySubKeyNames {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('CurrentUser', 'LocalMachine')]
        [string]$Hive,

        [Parameter(Mandatory = $true)]
        [ValidateSet('Default', 'Registry32', 'Registry64')]
        [string]$View,

        [Parameter(Mandatory = $true)]
        [string]$KeyName)

    Write-Host "Checking: hive '$Hive', view '$View', key name '$KeyName'"
    if ($View -eq 'Registry64' -and !([System.Environment]::Is64BitOperatingSystem)) {
        Write-Host "Skipping."
        return
    }

    $baseKey = $null
    $subKey = $null
    try {
        # Open the base key.
        $baseKey = [Microsoft.Win32.RegistryKey]::OpenBaseKey($Hive, $View)

        # Open the sub key as read-only.
        $subKey = $baseKey.OpenSubKey($KeyName, $false)

        # Check if the sub key was found.
        if (!$subKey) {
            Write-Host "Key not found."
            return
        }

        # Get the sub-key names.
        $subKeyNames = $subKey.GetSubKeyNames()
        Write-Host "Sub keys:"
        foreach ($subKeyName in $subKeyNames) {
            Write-Host "  '$subKeyName'"
        }

        return $subKeyNames
    } finally {
        # Dispose the sub key.
        if ($subKey) {
            $null = $subKey.Dispose()
        }

        # Dispose the base key.
        if ($baseKey) {
            $null = $baseKey.Dispose()
        }
    }
}

function Get-RegistryValue {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('CurrentUser', 'LocalMachine')]
        [string]$Hive,

        [Parameter(Mandatory = $true)]
        [ValidateSet('Default', 'Registry32', 'Registry64')]
        [string]$View,

        [Parameter(Mandatory = $true)]
        [string]$KeyName,

        [string]$ValueName)

    Write-Host "Checking: hive '$Hive', view '$View', key name '$KeyName', value name '$ValueName'"
    if ($View -eq 'Registry64' -and !([System.Environment]::Is64BitOperatingSystem)) {
        Write-Host "Skipping."
        return
    }

    $baseKey = $null
    $subKey = $null
    try {
        # Open the base key.
        $baseKey = [Microsoft.Win32.RegistryKey]::OpenBaseKey($Hive, $View)

        # Open the sub key as read-only.
        $subKey = $baseKey.OpenSubKey($KeyName, $false)

        # Check if the sub key was found.
        if (!$subKey) {
            Write-Host "Key not found."
            return
        }

        # Get the value.
        $value = $subKey.GetValue($ValueName)

        # Check if the value was not found or is empty.
        if ([System.Object]::ReferenceEquals($value, $null) -or
            ($value -is [string] -and !$value)) {

            Write-Host "Value not found or is empty."
            return
        }

        # Return the value.
        Write-Host "Found $($value.GetType().Name) value: '$value'"
        return $value
    } finally {
        # Dispose the sub key.
        if ($subKey) {
            $null = $subKey.Dispose()
        }

        # Dispose the base key.
        if ($baseKey) {
            $null = $baseKey.Dispose()
        }
    }
}

function Get-RegistryValueNames {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('CurrentUser', 'LocalMachine')]
        [string]$Hive,

        [Parameter(Mandatory = $true)]
        [ValidateSet('Default', 'Registry32', 'Registry64')]
        [string]$View,

        [Parameter(Mandatory = $true)]
        [string]$KeyName)

    Write-Host "Checking: hive '$Hive', view '$View', key name '$KeyName', value name '$ValueName'"
    if ($View -eq 'Registry64' -and !([System.Environment]::Is64BitOperatingSystem)) {
        Write-Host "Skipping."
        return
    }

    $baseKey = $null
    $subKey = $null
    try {
        # Open the base key.
        $baseKey = [Microsoft.Win32.RegistryKey]::OpenBaseKey($Hive, $View)

        # Open the sub key as read-only.
        $subKey = $baseKey.OpenSubKey($KeyName, $false)

        # Check if the sub key was found.
        if (!$subKey) {
            Write-Host "Key not found."
            return
        }

        # Get the value names.
        $valueNames = $subKey.GetValueNames()
        Write-Host "Value names:"
        foreach ($valueName in $valueNames) {
            Write-Host "  '$valueName'"
        }

        return $valueNames
    } finally {
        # Dispose the sub key.
        if ($subKey) {
            $null = $subKey.Dispose()
        }

        # Dispose the base key.
        if ($baseKey) {
            $null = $baseKey.Dispose()
        }
    }
}
# SIG # Begin signature block
# MIIoOQYJKoZIhvcNAQcCoIIoKjCCKCYCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQH8w7YFlLCE63JNLG
# KX7zUQIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCAGP4rSt8KJtfMH
# IAqrdcafNlUt9FW/c+5zs2b3MQm06qCCDYUwggYDMIID66ADAgECAhMzAAAEA73V
# lV0POxitAAAAAAQDMA0GCSqGSIb3DQEBCwUAMH4xCzAJBgNVBAYTAlVTMRMwEQYD
# VQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNy
# b3NvZnQgQ29ycG9yYXRpb24xKDAmBgNVBAMTH01pY3Jvc29mdCBDb2RlIFNpZ25p
# bmcgUENBIDIwMTEwHhcNMjQwOTEyMjAxMTEzWhcNMjUwOTExMjAxMTEzWjB0MQsw
# CQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9u
# ZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMR4wHAYDVQQDExVNaWNy
# b3NvZnQgQ29ycG9yYXRpb24wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIB
# AQCfdGddwIOnbRYUyg03O3iz19XXZPmuhEmW/5uyEN+8mgxl+HJGeLGBR8YButGV
# LVK38RxcVcPYyFGQXcKcxgih4w4y4zJi3GvawLYHlsNExQwz+v0jgY/aejBS2EJY
# oUhLVE+UzRihV8ooxoftsmKLb2xb7BoFS6UAo3Zz4afnOdqI7FGoi7g4vx/0MIdi
# kwTn5N56TdIv3mwfkZCFmrsKpN0zR8HD8WYsvH3xKkG7u/xdqmhPPqMmnI2jOFw/
# /n2aL8W7i1Pasja8PnRXH/QaVH0M1nanL+LI9TsMb/enWfXOW65Gne5cqMN9Uofv
# ENtdwwEmJ3bZrcI9u4LZAkujAgMBAAGjggGCMIIBfjAfBgNVHSUEGDAWBgorBgEE
# AYI3TAgBBggrBgEFBQcDAzAdBgNVHQ4EFgQU6m4qAkpz4641iK2irF8eWsSBcBkw
# VAYDVR0RBE0wS6RJMEcxLTArBgNVBAsTJE1pY3Jvc29mdCBJcmVsYW5kIE9wZXJh
# dGlvbnMgTGltaXRlZDEWMBQGA1UEBRMNMjMwMDEyKzUwMjkyNjAfBgNVHSMEGDAW
# gBRIbmTlUAXTgqoXNzcitW2oynUClTBUBgNVHR8ETTBLMEmgR6BFhkNodHRwOi8v
# d3d3Lm1pY3Jvc29mdC5jb20vcGtpb3BzL2NybC9NaWNDb2RTaWdQQ0EyMDExXzIw
# MTEtMDctMDguY3JsMGEGCCsGAQUFBwEBBFUwUzBRBggrBgEFBQcwAoZFaHR0cDov
# L3d3dy5taWNyb3NvZnQuY29tL3BraW9wcy9jZXJ0cy9NaWNDb2RTaWdQQ0EyMDEx
# XzIwMTEtMDctMDguY3J0MAwGA1UdEwEB/wQCMAAwDQYJKoZIhvcNAQELBQADggIB
# AFFo/6E4LX51IqFuoKvUsi80QytGI5ASQ9zsPpBa0z78hutiJd6w154JkcIx/f7r
# EBK4NhD4DIFNfRiVdI7EacEs7OAS6QHF7Nt+eFRNOTtgHb9PExRy4EI/jnMwzQJV
# NokTxu2WgHr/fBsWs6G9AcIgvHjWNN3qRSrhsgEdqHc0bRDUf8UILAdEZOMBvKLC
# rmf+kJPEvPldgK7hFO/L9kmcVe67BnKejDKO73Sa56AJOhM7CkeATrJFxO9GLXos
# oKvrwBvynxAg18W+pagTAkJefzneuWSmniTurPCUE2JnvW7DalvONDOtG01sIVAB
# +ahO2wcUPa2Zm9AiDVBWTMz9XUoKMcvngi2oqbsDLhbK+pYrRUgRpNt0y1sxZsXO
# raGRF8lM2cWvtEkV5UL+TQM1ppv5unDHkW8JS+QnfPbB8dZVRyRmMQ4aY/tx5x5+
# sX6semJ//FbiclSMxSI+zINu1jYerdUwuCi+P6p7SmQmClhDM+6Q+btE2FtpsU0W
# +r6RdYFf/P+nK6j2otl9Nvr3tWLu+WXmz8MGM+18ynJ+lYbSmFWcAj7SYziAfT0s
# IwlQRFkyC71tsIZUhBHtxPliGUu362lIO0Lpe0DOrg8lspnEWOkHnCT5JEnWCbzu
# iVt8RX1IV07uIveNZuOBWLVCzWJjEGa+HhaEtavjy6i7MIIHejCCBWKgAwIBAgIK
# YQ6Q0gAAAAAAAzANBgkqhkiG9w0BAQsFADCBiDELMAkGA1UEBhMCVVMxEzARBgNV
# BAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jv
# c29mdCBDb3Jwb3JhdGlvbjEyMDAGA1UEAxMpTWljcm9zb2Z0IFJvb3QgQ2VydGlm
# aWNhdGUgQXV0aG9yaXR5IDIwMTEwHhcNMTEwNzA4MjA1OTA5WhcNMjYwNzA4MjEw
# OTA5WjB+MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UE
# BxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSgwJgYD
# VQQDEx9NaWNyb3NvZnQgQ29kZSBTaWduaW5nIFBDQSAyMDExMIICIjANBgkqhkiG
# 9w0BAQEFAAOCAg8AMIICCgKCAgEAq/D6chAcLq3YbqqCEE00uvK2WCGfQhsqa+la
# UKq4BjgaBEm6f8MMHt03a8YS2AvwOMKZBrDIOdUBFDFC04kNeWSHfpRgJGyvnkmc
# 6Whe0t+bU7IKLMOv2akrrnoJr9eWWcpgGgXpZnboMlImEi/nqwhQz7NEt13YxC4D
# dato88tt8zpcoRb0RrrgOGSsbmQ1eKagYw8t00CT+OPeBw3VXHmlSSnnDb6gE3e+
# lD3v++MrWhAfTVYoonpy4BI6t0le2O3tQ5GD2Xuye4Yb2T6xjF3oiU+EGvKhL1nk
# kDstrjNYxbc+/jLTswM9sbKvkjh+0p2ALPVOVpEhNSXDOW5kf1O6nA+tGSOEy/S6
# A4aN91/w0FK/jJSHvMAhdCVfGCi2zCcoOCWYOUo2z3yxkq4cI6epZuxhH2rhKEmd
# X4jiJV3TIUs+UsS1Vz8kA/DRelsv1SPjcF0PUUZ3s/gA4bysAoJf28AVs70b1FVL
# 5zmhD+kjSbwYuER8ReTBw3J64HLnJN+/RpnF78IcV9uDjexNSTCnq47f7Fufr/zd
# sGbiwZeBe+3W7UvnSSmnEyimp31ngOaKYnhfsi+E11ecXL93KCjx7W3DKI8sj0A3
# T8HhhUSJxAlMxdSlQy90lfdu+HggWCwTXWCVmj5PM4TasIgX3p5O9JawvEagbJjS
# 4NaIjAsCAwEAAaOCAe0wggHpMBAGCSsGAQQBgjcVAQQDAgEAMB0GA1UdDgQWBBRI
# bmTlUAXTgqoXNzcitW2oynUClTAZBgkrBgEEAYI3FAIEDB4KAFMAdQBiAEMAQTAL
# BgNVHQ8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAfBgNVHSMEGDAWgBRyLToCMZBD
# uRQFTuHqp8cx0SOJNDBaBgNVHR8EUzBRME+gTaBLhklodHRwOi8vY3JsLm1pY3Jv
# c29mdC5jb20vcGtpL2NybC9wcm9kdWN0cy9NaWNSb29DZXJBdXQyMDExXzIwMTFf
# MDNfMjIuY3JsMF4GCCsGAQUFBwEBBFIwUDBOBggrBgEFBQcwAoZCaHR0cDovL3d3
# dy5taWNyb3NvZnQuY29tL3BraS9jZXJ0cy9NaWNSb29DZXJBdXQyMDExXzIwMTFf
# MDNfMjIuY3J0MIGfBgNVHSAEgZcwgZQwgZEGCSsGAQQBgjcuAzCBgzA/BggrBgEF
# BQcCARYzaHR0cDovL3d3dy5taWNyb3NvZnQuY29tL3BraW9wcy9kb2NzL3ByaW1h
# cnljcHMuaHRtMEAGCCsGAQUFBwICMDQeMiAdAEwAZQBnAGEAbABfAHAAbwBsAGkA
# YwB5AF8AcwB0AGEAdABlAG0AZQBuAHQALiAdMA0GCSqGSIb3DQEBCwUAA4ICAQBn
# 8oalmOBUeRou09h0ZyKbC5YR4WOSmUKWfdJ5DJDBZV8uLD74w3LRbYP+vj/oCso7
# v0epo/Np22O/IjWll11lhJB9i0ZQVdgMknzSGksc8zxCi1LQsP1r4z4HLimb5j0b
# pdS1HXeUOeLpZMlEPXh6I/MTfaaQdION9MsmAkYqwooQu6SpBQyb7Wj6aC6VoCo/
# KmtYSWMfCWluWpiW5IP0wI/zRive/DvQvTXvbiWu5a8n7dDd8w6vmSiXmE0OPQvy
# CInWH8MyGOLwxS3OW560STkKxgrCxq2u5bLZ2xWIUUVYODJxJxp/sfQn+N4sOiBp
# mLJZiWhub6e3dMNABQamASooPoI/E01mC8CzTfXhj38cbxV9Rad25UAqZaPDXVJi
# hsMdYzaXht/a8/jyFqGaJ+HNpZfQ7l1jQeNbB5yHPgZ3BtEGsXUfFL5hYbXw3MYb
# BL7fQccOKO7eZS/sl/ahXJbYANahRr1Z85elCUtIEJmAH9AAKcWxm6U/RXceNcbS
# oqKfenoi+kiVH6v7RyOA9Z74v2u3S5fi63V4GuzqN5l5GEv/1rMjaHXmr/r8i+sL
# gOppO6/8MO0ETI7f33VtY5E90Z1WTk+/gFcioXgRMiF670EKsT/7qMykXcGhiJtX
# cVZOSEXAQsmbdlsKgEhr/Xmfwb1tbWrJUnMTDXpQzTGCGgowghoGAgEBMIGVMH4x
# CzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRt
# b25kMR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xKDAmBgNVBAMTH01p
# Y3Jvc29mdCBDb2RlIFNpZ25pbmcgUENBIDIwMTECEzMAAAQDvdWVXQ87GK0AAAAA
# BAMwDQYJYIZIAWUDBAIBBQCgga4wGQYJKoZIhvcNAQkDMQwGCisGAQQBgjcCAQQw
# HAYKKwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkEMSIEIHTy
# V3S7+7oqoDEF7oYiSL1bumvpNNWDjWZZZDWdG+ZSMEIGCisGAQQBgjcCAQwxNDAy
# oBSAEgBNAGkAYwByAG8AcwBvAGYAdKEagBhodHRwOi8vd3d3Lm1pY3Jvc29mdC5j
# b20wDQYJKoZIhvcNAQEBBQAEggEAkCZ2T/SENAXDDxC/8GALckDP1K6sZTQrkQuk
# bl52WhN8S8RiyyVO0z9vzGP7mftCbYslxDNT1SD3mauXNZm795T5YdOR0lhAewX/
# z31E4S1bKiMwVT+VdvJ+qXirvhaktvTgv6IrrfTS+bCEjBWbu+t5GC0Vqce8BBpU
# Tq65tRCjVsHlKu3N5SbRvw9xoC53yB2u+1uxhvzpmzpz7/ygn2VjO8DbDLmkEljz
# h2QCXLR3LHZEyM+CTaUDliI/t6QpVTt0WRS35tJyX1+qJvApuYz7GAAhitvPy4I9
# 8ID5ZiZKtZ83tV7LneWQWzc8hSKMxGZCt38kjIJuZUCIa7h+XKGCF5QwgheQBgor
# BgEEAYI3AwMBMYIXgDCCF3wGCSqGSIb3DQEHAqCCF20wghdpAgEDMQ8wDQYJYIZI
# AWUDBAIBBQAwggFSBgsqhkiG9w0BCRABBKCCAUEEggE9MIIBOQIBAQYKKwYBBAGE
# WQoDATAxMA0GCWCGSAFlAwQCAQUABCDuhgtPvp1cx5AjrzbRQr7Fp8dcT9gNlGwp
# naKuZLZtaAIGaEsE3lxAGBMyMDI1MDcwMzEwMzI0My4zNThaMASAAgH0oIHRpIHO
# MIHLMQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMH
# UmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQL
# ExxNaWNyb3NvZnQgQW1lcmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxk
# IFRTUyBFU046REMwMC0wNUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1l
# LVN0YW1wIFNlcnZpY2WgghHqMIIHIDCCBQigAwIBAgITMwAAAgO7HlwAOGx0ygAB
# AAACAzANBgkqhkiG9w0BAQsFADB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2Fz
# aGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENv
# cnBvcmF0aW9uMSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAx
# MDAeFw0yNTAxMzAxOTQyNDZaFw0yNjA0MjIxOTQyNDZaMIHLMQswCQYDVQQGEwJV
# UzETMBEGA1UECBMKV2FzaGluZ3RvbjEQMA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UE
# ChMVTWljcm9zb2Z0IENvcnBvcmF0aW9uMSUwIwYDVQQLExxNaWNyb3NvZnQgQW1l
# cmljYSBPcGVyYXRpb25zMScwJQYDVQQLEx5uU2hpZWxkIFRTUyBFU046REMwMC0w
# NUUwLUQ5NDcxJTAjBgNVBAMTHE1pY3Jvc29mdCBUaW1lLVN0YW1wIFNlcnZpY2Uw
# ggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQChl0MH5wAnOx8Uh8RtidF0
# J0yaFDHJYHTpPvRR16X1KxGDYfT8PrcGjCLCiaOu3K1DmUIU4Rc5olndjappNuOg
# zwUoj43VbbJx5PFTY/a1Z80tpqVP0OoKJlUkfDPSBLFgXWj6VgayRCINtLsUasy0
# w5gysD7ILPZuiQjace5KxASjKf2MVX1qfEzYBbTGNEijSQCKwwyc0eavr4Fo3X/+
# sCuuAtkTWissU64k8rK60jsGRApiESdfuHr0yWAmc7jTOPNeGAx6KCL2ktpnGegL
# Dd1IlE6Bu6BSwAIFHr7zOwIlFqyQuCe0SQALCbJhsT9y9iy61RJAXsU0u0TC5YYm
# TSbEI7g10dYx8Uj+vh9InLoKYC5DpKb311bYVd0bytbzlfTRslRTJgotnfCAIGML
# qEqk9/2VRGu9klJi1j9nVfqyYHYrMPOBXcrQYW0jmKNjOL47CaEArNzhDBia1wXd
# JANKqMvJ8pQe2m8/cibyDM+1BVZquNAov9N4tJF4ACtjX0jjXNDUMtSZoVFQH+Fk
# WdfPWx1uBIkc97R+xRLuPjUypHZ5A3AALSke4TaRBvbvTBYyW2HenOT7nYLKTO4j
# w5Qq6cw3Z9zTKSPQ6D5lyiYpes5RR2MdMvJS4fCcPJFeaVOvuWFSQ/EGtVBShhmL
# B+5ewzFzdpf1UuJmuOQTTwIDAQABo4IBSTCCAUUwHQYDVR0OBBYEFLIpWUB+EeeQ
# 29sWe0VdzxWQGJJ9MB8GA1UdIwQYMBaAFJ+nFV0AXmJdg/Tl0mWnG1M1GelyMF8G
# A1UdHwRYMFYwVKBSoFCGTmh0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9wa2lvcHMv
# Y3JsL01pY3Jvc29mdCUyMFRpbWUtU3RhbXAlMjBQQ0ElMjAyMDEwKDEpLmNybDBs
# BggrBgEFBQcBAQRgMF4wXAYIKwYBBQUHMAKGUGh0dHA6Ly93d3cubWljcm9zb2Z0
# LmNvbS9wa2lvcHMvY2VydHMvTWljcm9zb2Z0JTIwVGltZS1TdGFtcCUyMFBDQSUy
# MDIwMTAoMSkuY3J0MAwGA1UdEwEB/wQCMAAwFgYDVR0lAQH/BAwwCgYIKwYBBQUH
# AwgwDgYDVR0PAQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4ICAQCQEMbesD6TC08R
# 0oYCdSC452AQrGf/O89GQ54CtgEsbxzwGDVUcmjXFcnaJSTNedBKVXkBgawRonP1
# LgxH4bzzVj2eWNmzGIwO1FlhldAPOHAzLBEHRoSZ4pddFtaQxoabU/N1vWyICiN6
# 0It85gnF5JD4MMXyd6pS8eADIi6TtjfgKPoumWa0BFQ/aEzjUrfPN1r7crK+qkmL
# ztw/ENS7zemfyx4kGRgwY1WBfFqm/nFlJDPQBicqeU3dOp9hj7WqD0Rc+/4VZ6wQ
# jesIyCkv5uhUNy2LhNDi2leYtAiIFpmjfNk4GngLvC2Tj9IrOMv20Srym5J/Fh7y
# WAiPeGs3yA3QapjZTtfr7NfzpBIJQ4xT/ic4WGWqhGlRlVBI5u6Ojw3ZxSZCLg3v
# RC4KYypkh8FdIWoKirjidEGlXsNOo+UP/YG5KhebiudTBxGecfJCuuUspIdRhStH
# AQsjv/dAqWBLlhorq2OCaP+wFhE3WPgnnx5pflvlujocPgsN24++ddHrl3O1FFab
# W8m0UkDHSKCh8QTwTkYOwu99iExBVWlbYZRz2qOIBjL/ozEhtCB0auKhfTLLeuNG
# BUaBz+oZZ+X9UAECoMhkETjb6YfNaI1T7vVAaiuhBoV/JCOQT+RYZrgykyPpzpmw
# MNFBD1vdW/29q9nkTWoEhcEOO0L9NzCCB3EwggVZoAMCAQICEzMAAAAVxedrngKb
# SZkAAAAAABUwDQYJKoZIhvcNAQELBQAwgYgxCzAJBgNVBAYTAlVTMRMwEQYDVQQI
# EwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25kMR4wHAYDVQQKExVNaWNyb3Nv
# ZnQgQ29ycG9yYXRpb24xMjAwBgNVBAMTKU1pY3Jvc29mdCBSb290IENlcnRpZmlj
# YXRlIEF1dGhvcml0eSAyMDEwMB4XDTIxMDkzMDE4MjIyNVoXDTMwMDkzMDE4MzIy
# NVowfDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcT
# B1JlZG1vbmQxHjAcBgNVBAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UE
# AxMdTWljcm9zb2Z0IFRpbWUtU3RhbXAgUENBIDIwMTAwggIiMA0GCSqGSIb3DQEB
# AQUAA4ICDwAwggIKAoICAQDk4aZM57RyIQt5osvXJHm9DtWC0/3unAcH0qlsTnXI
# yjVX9gF/bErg4r25PhdgM/9cT8dm95VTcVrifkpa/rg2Z4VGIwy1jRPPdzLAEBjo
# YH1qUoNEt6aORmsHFPPFdvWGUNzBRMhxXFExN6AKOG6N7dcP2CZTfDlhAnrEqv1y
# aa8dq6z2Nr41JmTamDu6GnszrYBbfowQHJ1S/rboYiXcag/PXfT+jlPP1uyFVk3v
# 3byNpOORj7I5LFGc6XBpDco2LXCOMcg1KL3jtIckw+DJj361VI/c+gVVmG1oO5pG
# ve2krnopN6zL64NF50ZuyjLVwIYwXE8s4mKyzbnijYjklqwBSru+cakXW2dg3viS
# kR4dPf0gz3N9QZpGdc3EXzTdEonW/aUgfX782Z5F37ZyL9t9X4C626p+Nuw2TPYr
# bqgSUei/BQOj0XOmTTd0lBw0gg/wEPK3Rxjtp+iZfD9M269ewvPV2HM9Q07BMzlM
# jgK8QmguEOqEUUbi0b1qGFphAXPKZ6Je1yh2AuIzGHLXpyDwwvoSCtdjbwzJNmSL
# W6CmgyFdXzB0kZSU2LlQ+QuJYfM2BjUYhEfb3BvR/bLUHMVr9lxSUV0S2yW6r1AF
# emzFER1y7435UsSFF5PAPBXbGjfHCBUYP3irRbb1Hode2o+eFnJpxq57t7c+auIu
# rQIDAQABo4IB3TCCAdkwEgYJKwYBBAGCNxUBBAUCAwEAATAjBgkrBgEEAYI3FQIE
# FgQUKqdS/mTEmr6CkTxGNSnPEP8vBO4wHQYDVR0OBBYEFJ+nFV0AXmJdg/Tl0mWn
# G1M1GelyMFwGA1UdIARVMFMwUQYMKwYBBAGCN0yDfQEBMEEwPwYIKwYBBQUHAgEW
# M2h0dHA6Ly93d3cubWljcm9zb2Z0LmNvbS9wa2lvcHMvRG9jcy9SZXBvc2l0b3J5
# Lmh0bTATBgNVHSUEDDAKBggrBgEFBQcDCDAZBgkrBgEEAYI3FAIEDB4KAFMAdQBi
# AEMAQTALBgNVHQ8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAfBgNVHSMEGDAWgBTV
# 9lbLj+iiXGJo0T2UkFvXzpoYxDBWBgNVHR8ETzBNMEugSaBHhkVodHRwOi8vY3Js
# Lm1pY3Jvc29mdC5jb20vcGtpL2NybC9wcm9kdWN0cy9NaWNSb29DZXJBdXRfMjAx
# MC0wNi0yMy5jcmwwWgYIKwYBBQUHAQEETjBMMEoGCCsGAQUFBzAChj5odHRwOi8v
# d3d3Lm1pY3Jvc29mdC5jb20vcGtpL2NlcnRzL01pY1Jvb0NlckF1dF8yMDEwLTA2
# LTIzLmNydDANBgkqhkiG9w0BAQsFAAOCAgEAnVV9/Cqt4SwfZwExJFvhnnJL/Klv
# 6lwUtj5OR2R4sQaTlz0xM7U518JxNj/aZGx80HU5bbsPMeTCj/ts0aGUGCLu6WZn
# OlNN3Zi6th542DYunKmCVgADsAW+iehp4LoJ7nvfam++Kctu2D9IdQHZGN5tggz1
# bSNU5HhTdSRXud2f8449xvNo32X2pFaq95W2KFUn0CS9QKC/GbYSEhFdPSfgQJY4
# rPf5KYnDvBewVIVCs/wMnosZiefwC2qBwoEZQhlSdYo2wh3DYXMuLGt7bj8sCXgU
# 6ZGyqVvfSaN0DLzskYDSPeZKPmY7T7uG+jIa2Zb0j/aRAfbOxnT99kxybxCrdTDF
# NLB62FD+CljdQDzHVG2dY3RILLFORy3BFARxv2T5JL5zbcqOCb2zAVdJVGTZc9d/
# HltEAY5aGZFrDZ+kKNxnGSgkujhLmm77IVRrakURR6nxt67I6IleT53S0Ex2tVdU
# CbFpAUR+fKFhbHP+CrvsQWY9af3LwUFJfn6Tvsv4O+S3Fb+0zj6lMVGEvL8CwYKi
# excdFYmNcP7ntdAoGokLjzbaukz5m/8K6TT4JDVnK+ANuOaMmdbhIurwJ0I9JZTm
# dHRbatGePu1+oDEzfbzL6Xu/OHBE0ZDxyKs6ijoIYn/ZcGNTTY3ugm2lBRDBcQZq
# ELQdVTNYs6FwZvKhggNNMIICNQIBATCB+aGB0aSBzjCByzELMAkGA1UEBhMCVVMx
# EzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAcBgNVBAoT
# FU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjElMCMGA1UECxMcTWljcm9zb2Z0IEFtZXJp
# Y2EgT3BlcmF0aW9uczEnMCUGA1UECxMeblNoaWVsZCBUU1MgRVNOOkRDMDAtMDVF
# MC1EOTQ3MSUwIwYDVQQDExxNaWNyb3NvZnQgVGltZS1TdGFtcCBTZXJ2aWNloiMK
# AQEwBwYFKw4DAhoDFQDNrxRX/iz6ss1lBCXG8P1LFxD0e6CBgzCBgKR+MHwxCzAJ
# BgNVBAYTAlVTMRMwEQYDVQQIEwpXYXNoaW5ndG9uMRAwDgYDVQQHEwdSZWRtb25k
# MR4wHAYDVQQKExVNaWNyb3NvZnQgQ29ycG9yYXRpb24xJjAkBgNVBAMTHU1pY3Jv
# c29mdCBUaW1lLVN0YW1wIFBDQSAyMDEwMA0GCSqGSIb3DQEBCwUAAgUA7BCITDAi
# GA8yMDI1MDcwMzA0NDA0NFoYDzIwMjUwNzA0MDQ0MDQ0WjB0MDoGCisGAQQBhFkK
# BAExLDAqMAoCBQDsEIhMAgEAMAcCAQACAgCaMAcCAQACAhLxMAoCBQDsEdnMAgEA
# MDYGCisGAQQBhFkKBAIxKDAmMAwGCisGAQQBhFkKAwKgCjAIAgEAAgMHoSChCjAI
# AgEAAgMBhqAwDQYJKoZIhvcNAQELBQADggEBAHD9twX/iNakPZ1hfYsuh96A1kkz
# t0+tTX+VgvCRvfhfEveazYBsJcpCr0i6A8drgZcrv4t5d5bDRX4rEqVwH6lkBfSH
# pNunfQ7MMhYYdY177VUolAt3+elMO+il4qwRCl3LnDaYPUbB9xi6p8JSU9yUCr8A
# Xb1IhDGsTCNJJ0y7y7h6HWecAzcacMs5Y4b1N36laO/nqz6f5hl3SX42nQcJYh4E
# UN/QbZgQPqZvVXHFY715mRdo7FOLnuuYKdTkqWysevdt6pk3/ao5DFIc/Utsn2rS
# b/ciF3rgwLL8Upc2diFPISeiPIwAXy8cRWJApJcgkN6F8T0IimPV7WKCdJcxggQN
# MIIECQIBATCBkzB8MQswCQYDVQQGEwJVUzETMBEGA1UECBMKV2FzaGluZ3RvbjEQ
# MA4GA1UEBxMHUmVkbW9uZDEeMBwGA1UEChMVTWljcm9zb2Z0IENvcnBvcmF0aW9u
# MSYwJAYDVQQDEx1NaWNyb3NvZnQgVGltZS1TdGFtcCBQQ0EgMjAxMAITMwAAAgO7
# HlwAOGx0ygABAAACAzANBglghkgBZQMEAgEFAKCCAUowGgYJKoZIhvcNAQkDMQ0G
# CyqGSIb3DQEJEAEEMC8GCSqGSIb3DQEJBDEiBCACxoGUtKEkreKNSu9/IvvkY0+U
# 3UqX+AzDJd+y9llh3jCB+gYLKoZIhvcNAQkQAi8xgeowgecwgeQwgb0EIEsD3Rtx
# lvaTxFOZZnpQw0DksPmVduo5SyK9h9w++hMtMIGYMIGApH4wfDELMAkGA1UEBhMC
# VVMxEzARBgNVBAgTCldhc2hpbmd0b24xEDAOBgNVBAcTB1JlZG1vbmQxHjAcBgNV
# BAoTFU1pY3Jvc29mdCBDb3Jwb3JhdGlvbjEmMCQGA1UEAxMdTWljcm9zb2Z0IFRp
# bWUtU3RhbXAgUENBIDIwMTACEzMAAAIDux5cADhsdMoAAQAAAgMwIgQgLVPsXuo+
# YcHL6s5cAjojGM9vHM8dxvJFTKOAWUjnCMQwDQYJKoZIhvcNAQELBQAEggIAeJut
# qNnuWPcC+BkzrLnTlrGWfDeMdlqdb/7yka2ziUQN95YEYcDGofN4P4VN4lOQ5poH
# 95IYBTP9YPmPGz3F/2qVs/rPXjKMo29z/sL9Yu7VGZYoKgFI00BbrGqh0VSEtXMe
# jyhEFTkay3CkLlS/FwbG89XUAI976baSA1XLuGAd+hWYnpzF/DMYLiwc5XNFtoH2
# cRSx6/nobRat1HkBJ6nMA2euzhCRzoj3iZqc/X6iFuLHV65wFAgGDmRRKaBu1mFG
# DNDkmswcbFqOXYk+LXmfaFFZQYYYfP389cGUvqQLiVzC1qISvU6ZGwCd6ra/cLH+
# aDHGFgcmZTtoKOTETQwDbtpKZo5qpecdPDNfDDt8gzoi91ccsjfP7EQLoNKNhVE7
# /e0+7Ed4pDLt4MnPAZiWPAwuc+3jc6LLuAtlht+s0dVNH9yd3NvGm6cJ69VTSf5H
# QeRjNNclIh8sbFYmVRwcySuPk7NSExsH9Ifz3SOe9ID13RXsyl6ht//Z7U6UCAsZ
# roCR/FYsB9DqT3RyOeMiyjmBo/1Vk7Ip8djp13wT1shtwallzcvT62JVLrOtcvQq
# IqUmD9Bfs+rPK82rHlQ49HzkOay4QW2aAyC2fJ6KJ862IN7xzdl7RpGDnX7uGNRz
# nE8Tfru2N5uyFHbsp/qgQLNIbMSVwVRQwSBy02g=
# SIG # End signature block
