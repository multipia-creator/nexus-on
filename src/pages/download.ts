/**
 * NEXUS-ON Windows Download Page
 * Ported from public/downloads/windows/index.html
 */

import type { Language } from '../../shared/types'
import { t } from '../../shared/i18n'
import { renderNavigation } from '../components/navigation'
import { renderFooter } from '../components/footer'
import { getGlobalStyles } from '../../shared/styles'

export function downloadPage(lang: Language = 'ko'): string {
  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NEXUS Engine - Windows ${t('download_page_title', lang)}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css" rel="stylesheet">
        <style>${renderWorldClassStyles()}</style>
    </head>
    <body class="bg-gray-50">
        ${renderNavigation(lang)}
        
        <div class="max-w-4xl mx-auto py-16 px-4">
            <div class="text-center mb-12">
                <h1 class="text-4xl font-bold text-gray-900 mb-4">
                    <i class="fas fa-download text-blue-600 mr-3"></i>
                    NEXUS Engine for Windows
                </h1>
                <p class="text-xl text-gray-600">
                    ${t('download_page_subtitle', lang)}
                </p>
            </div>

            <div class="grid md:grid-cols-2 gap-6 mb-12">
                <!-- Setup.exe -->
                <div class="bg-white rounded-lg shadow-lg p-6 border-2 border-blue-500">
                    <div class="text-center mb-4">
                        <i class="fas fa-box-archive text-5xl text-blue-600 mb-3"></i>
                        <h3 class="text-2xl font-bold text-gray-900">Setup.exe</h3>
                        <p class="text-gray-600 mt-2">${t('download_setup_desc', lang)}</p>
                    </div>
                    <ul class="space-y-2 mb-6 text-sm text-gray-700">
                        <li><i class="fas fa-check text-green-600 mr-2"></i>${t('download_setup_feature_1', lang)}</li>
                        <li><i class="fas fa-check text-green-600 mr-2"></i>${t('download_setup_feature_2', lang)}</li>
                        <li><i class="fas fa-check text-green-600 mr-2"></i>${t('download_setup_feature_3', lang)}</li>
                        <li><i class="fas fa-check text-green-600 mr-2"></i>${t('download_setup_feature_4', lang)}</li>
                    </ul>
                    <a href="/downloads/windows/NEXUS-Engine-Windows-x64-Setup.exe" 
                       class="block w-full bg-blue-600 text-white text-center py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
                        <i class="fas fa-download mr-2"></i>${t('download_button', lang)}
                    </a>
                    <p class="text-xs text-gray-500 mt-3 text-center">
                        <i class="fas fa-info-circle mr-1"></i>
                        ${t('download_setup_note', lang)}
                    </p>
                </div>

                <!-- PowerShell Script -->
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <div class="text-center mb-4">
                        <i class="fas fa-terminal text-5xl text-purple-600 mb-3"></i>
                        <h3 class="text-2xl font-bold text-gray-900">PowerShell</h3>
                        <p class="text-gray-600 mt-2">${t('download_powershell_desc', lang)}</p>
                    </div>
                    <ul class="space-y-2 mb-6 text-sm text-gray-700">
                        <li><i class="fas fa-check text-green-600 mr-2"></i>${t('download_powershell_feature_1', lang)}</li>
                        <li><i class="fas fa-check text-green-600 mr-2"></i>${t('download_powershell_feature_2', lang)}</li>
                        <li><i class="fas fa-check text-green-600 mr-2"></i>${t('download_powershell_feature_3', lang)}</li>
                        <li><i class="fas fa-check text-green-600 mr-2"></i>${t('download_powershell_feature_4', lang)}</li>
                    </ul>
                    <button onclick="copyScript()" 
                            class="block w-full bg-purple-600 text-white text-center py-3 rounded-lg font-semibold hover:bg-purple-700 transition">
                        <i class="fas fa-copy mr-2"></i>${t('download_copy_script', lang)}
                    </button>
                </div>
            </div>

            <!-- System Requirements -->
            <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
                <h3 class="text-xl font-bold text-gray-900 mb-4">
                    <i class="fas fa-laptop text-blue-600 mr-2"></i>${t('download_requirements', lang)}
                </h3>
                <div class="grid md:grid-cols-3 gap-4">
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-2">${t('download_req_os', lang)}</h4>
                        <p class="text-sm text-gray-600">Windows 10/11 (64-bit)</p>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-2">${t('download_req_memory', lang)}</h4>
                        <p class="text-sm text-gray-600">${t('download_req_memory_value', lang)}</p>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-2">${t('download_req_storage', lang)}</h4>
                        <p class="text-sm text-gray-600">${t('download_req_storage_value', lang)}</p>
                    </div>
                </div>
            </div>

            <!-- Quick Start -->
            <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
                <h3 class="text-xl font-bold text-gray-900 mb-4">
                    <i class="fas fa-rocket text-blue-600 mr-2"></i>${t('download_quick_start', lang)}
                </h3>
                <ol class="space-y-3 text-sm text-gray-700">
                    <li><span class="font-semibold">1.</span> ${t('download_step_1', lang)}</li>
                    <li><span class="font-semibold">2.</span> ${t('download_step_2', lang)}</li>
                    <li><span class="font-semibold">3.</span> ${t('download_step_3', lang)} <code class="bg-white px-2 py-1 rounded">http://localhost:7100</code></li>
                    <li><span class="font-semibold">4.</span> ${t('download_step_4', lang)} <a href="https://nexus-3bm.pages.dev" class="text-blue-600 underline">nexus-3bm.pages.dev</a></li>
                </ol>
            </div>

            <!-- Links -->
            <div class="mt-8 text-center space-x-4">
                <a href="/downloads/windows/INSTALLATION_GUIDE.md" class="text-blue-600 hover:underline">
                    <i class="fas fa-book mr-1"></i>${t('download_guide', lang)}
                </a>
                <a href="/downloads/windows/BUILD_INSTRUCTIONS.md" class="text-blue-600 hover:underline">
                    <i class="fas fa-code mr-1"></i>${t('download_build', lang)}
                </a>
                <a href="https://github.com/multipia-creator/nexus-on" class="text-blue-600 hover:underline" target="_blank">
                    <i class="fab fa-github mr-1"></i>GitHub
                </a>
            </div>
        </div>

        ${renderFooter(lang)}

        <script>
        function copyScript() {
            const script = "Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://nexus-3bm.pages.dev/downloads/windows/bootstrap.ps1'))";
            navigator.clipboard.writeText(script).then(() => {
                alert('✅ ${t('download_copy_success', lang)}');
            });
        }
        </script>
    </body>
    </html>
  `
}
