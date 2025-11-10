document.addEventListener('DOMContentLoaded', function() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('inputArchivo');
    const fileName = document.getElementById('fileName');
    const form = document.getElementById('evidenciaForm');
    const btnSubir = document.getElementById('btnSubir');

    // Drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.remove('dragover'), false);
    });

    uploadZone.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        mostrarNombreArchivo(files[0]);
    });

    uploadZone.addEventListener('click', function(e) {
        if (e.target !== fileInput) {
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            mostrarNombreArchivo(this.files[0]);
        }
    });

    function mostrarNombreArchivo(file) {
        const size = (file.size / 1024 / 1024).toFixed(2);
        fileName.innerHTML = `<i class="fas fa-file"></i> ${file.name} (${size} MB)`;
    }

    // Subida con AJAX
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        btnSubir.disabled = true;
        btnSubir.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Subiendo...';

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Agregar nueva evidencia al DOM
                agregarEvidenciaAlDOM(data.evidencia);
                form.reset();
                fileName.innerHTML = '';
                
                // Ocultar mensaje de "No hay evidencias"
                const noEvidencias = document.getElementById('noEvidencias');
                if (noEvidencias) noEvidencias.remove();
                
                // Mostrar mensaje de éxito
                mostrarMensaje('Evidencia subida correctamente', 'success');
            } else {
                let errorMsg = 'Error al subir la evidencia';
                if (data.errors) {
                    const errorValues = Object.values(data.errors).flat();
                    errorMsg += ': ' + errorValues.join(', ');
                }
                mostrarMensaje(errorMsg, 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarMensaje('Error al subir la evidencia', 'danger');
        })
        .finally(() => {
            btnSubir.disabled = false;
            btnSubir.innerHTML = '<i class="fas fa-upload"></i> Subir Evidencia';
        });
    });

    function agregarEvidenciaAlDOM(evidencia) {
        const container = document.getElementById('evidenciasContainer');
        const card = document.createElement('div');
        card.className = 'evidencia-card';
        card.dataset.evidenciaId = evidencia.id;
        
        let preview = '';
        if (evidencia.tipo === 'imagen') {
            preview = `<img src="${evidencia.url}" class="evidencia-preview" alt="${evidencia.nombre}">`;
        } else if (evidencia.tipo === 'video') {
            preview = `<video controls class="evidencia-preview"><source src="${evidencia.url}" type="video/${evidencia.formato}"></video>`;
        } else if (evidencia.tipo === 'audio') {
            preview = `<div class="evidencia-icono">🎵</div><audio controls class="w-100"><source src="${evidencia.url}" type="audio/${evidencia.formato}"></audio>`;
        } else {
            preview = `<div class="evidencia-icono">${evidencia.icono}</div><a href="${evidencia.url}" target="_blank" class="btn btn-sm btn-outline-primary w-100"><i class="fas fa-download"></i> Descargar ${evidencia.formato.toUpperCase()}</a>`;
        }
        
        const tamanioStr = evidencia.tamanio ? ` • ${formatBytes(evidencia.tamanio)}` : '';
        
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <h6 class="mb-0">${evidencia.icono} ${evidencia.nombre}</h6>
                <button class="btn btn-sm btn-danger btn-eliminar" 
                        data-evidencia-id="${evidencia.id}"
                        data-evidencia-nombre="${evidencia.nombre}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            ${preview}
            <div class="evidencia-info">
                <small class="text-muted">
                    ${evidencia.formato.toUpperCase()}${tamanioStr} • Recién subido
                </small>
            </div>
        `;
        
        container.insertBefore(card, container.firstChild);
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    function mostrarMensaje(texto, tipo) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${tipo} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${texto}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Eliminar evidencia
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-eliminar')) {
            const btn = e.target.closest('.btn-eliminar');
            const evidenciaId = btn.dataset.evidenciaId;
            const evidenciaNombre = btn.dataset.evidenciaNombre;
            
            const modal = new bootstrap.Modal(document.getElementById('modalEliminar'));
            document.getElementById('evidenciaNombre').textContent = evidenciaNombre;
            
            const formEliminar = document.getElementById('formEliminar');
            formEliminar.action = `/territorial/evidencia/${evidenciaId}/eliminar/`;
            
            formEliminar.onsubmit = function(e) {
                e.preventDefault();
                
                fetch(formEliminar.action, {
                    method: 'POST',
                    body: new FormData(formEliminar),
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Eliminar del DOM
                        const card = document.querySelector(`[data-evidencia-id="${evidenciaId}"]`);
                        if (card) card.remove();
                        
                        // Si no quedan evidencias, mostrar mensaje
                        const container = document.getElementById('evidenciasContainer');
                        if (container.children.length === 0) {
                            container.innerHTML = `
                                <div class="text-center text-muted py-5" id="noEvidencias">
                                    <i class="fas fa-folder-open fa-3x mb-3"></i>
                                    <p>No hay evidencias subidas aún</p>
                                </div>
                            `;
                        }
                        
                        modal.hide();
                        mostrarMensaje(data.message, 'success');
                    } else {
                        mostrarMensaje('Error al eliminar la evidencia', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    mostrarMensaje('Error al eliminar la evidencia', 'danger');
                });
            };
            
            modal.show();
        }
    });
});