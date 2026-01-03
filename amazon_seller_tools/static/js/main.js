// 主要JavaScript功能

// API调用辅助函数
async function apiCall(endpoint, data) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API调用错误:', error);
        return { success: false, error: error.message };
    }
}

// 显示加载状态
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading"><div class="spinner"></div><p>正在分析...</p></div>';
        element.classList.remove('hidden');
    }
}

// 隐藏加载状态
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('hidden');
    }
}

// 显示结果
function showResult(elementId, content) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = content;
        element.classList.remove('hidden');
    }
}

// 格式化货币
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// 格式化百分比
function formatPercent(value) {
    return value.toFixed(1) + '%';
}

// 格式化数字
function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

// 获取颜色类
function getColorClass(value, thresholds) {
    if (value >= thresholds.good) return 'positive';
    if (value >= thresholds.warning) return 'warning';
    return 'negative';
}

// 表单验证
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = '#ef4444';
            isValid = false;
        } else {
            input.style.borderColor = '#ddd';
        }
    });
    
    return isValid;
}

// 显示错误消息
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = 'background: #fee; border-left: 4px solid #ef4444; padding: 1rem; margin: 1rem 0; border-radius: 5px;';
    errorDiv.innerHTML = `<strong>错误：</strong> ${message}`;
    
    const container = document.querySelector('.main-content');
    if (container) {
        container.insertBefore(errorDiv, container.firstChild);
        setTimeout(() => errorDiv.remove(), 5000);
    }
}

// 显示成功消息
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.style.cssText = 'background: #d1fae5; border-left: 4px solid #10b981; padding: 1rem; margin: 1rem 0; border-radius: 5px;';
    successDiv.innerHTML = `<strong>成功：</strong> ${message}`;
    
    const container = document.querySelector('.main-content');
    if (container) {
        container.insertBefore(successDiv, container.firstChild);
        setTimeout(() => successDiv.remove(), 5000);
    }
}

// 导出为CSV
function exportToCSV(data, filename) {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 转换为CSV
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [];
    
    // 添加表头
    csvRows.push(headers.join(','));
    
    // 添加数据行
    for (const row of data) {
        const values = headers.map(header => {
            const value = row[header];
            return typeof value === 'string' ? `"${value}"` : value;
        });
        csvRows.push(values.join(','));
    }
    
    return csvRows.join('\n');
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('亚马逊卖家智能辅助系统已加载');
    
    // 给所有导航链接添加活动状态
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
});

// 导出函数供其他页面使用
window.amazonTools = {
    apiCall,
    showLoading,
    hideLoading,
    showResult,
    formatCurrency,
    formatPercent,
    formatNumber,
    getColorClass,
    validateForm,
    showError,
    showSuccess,
    exportToCSV
};
