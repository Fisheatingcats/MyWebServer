
            /* 设备类型分组样式 */
            .device-type-group {
                margin-bottom: 30px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
                background-color: #f9f9f9;
            }

            .device-type-header {
                padding: 15px 20px;
                background-color: #2c3e50;
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }

            .device-type-header:hover {
                background-color: #34495e;
            }

            .device-type-title {
                font-size: 18px;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .device-type-count {
                background-color: rgba(255, 255, 255, 0.2);
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: normal;
            }

            .device-type-content {
                padding: 20px;
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
            }

            .type-action-buttons {
                display: flex;
                gap: 10px;
            }

            .btn-group-action {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.3s ease;
            }

            .btn-group-action:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }

            /* 加载动画样式 */
            .loading {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* 创建设备类型模态框样式 */
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0,0,0,0.4);
                transition: opacity 0.3s ease;
            }

            .modal-content {
                background-color: #fefefe;
                margin: 10% auto;
                padding: 20px;
                border: 1px solid #888;
                border-radius: 8px;
                width: 90%;
                max-width: 500px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                animation: modal-appear 0.3s ease-out;
            }

            @keyframes modal-appear {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }

            .close:hover,
            .close:focus {
                color: black;
                text-decoration: none;
            }

            .modal-header {
                padding-bottom: 15px;
                border-bottom: 1px solid #e0e0e0;
                margin-bottom: 20px;
            }

            .modal-title {
                margin: 0;
                font-size: 20px;
                font-weight: 500;
            }

            .modal-body {
                margin-bottom: 20px;
            }

            .form-group {
                margin-bottom: 15px;
            }

            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
            }

            .form-control {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                transition: border-color 0.3s ease;
            }

            .form-control:focus {
                border-color: #2c3e50;
                outline: none;
            }

            .modal-footer {
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                display: flex;
                justify-content: flex-end;
                gap: 10px;
            }

            .btn-submit {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.3s ease;
            }

            .btn-submit:hover {
                background-color: #34495e;
            }

            .btn-cancel {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.3s ease;
            }

            .btn-cancel:hover {
                background-color: #7f8c8d;
            }

            .btn-submit:disabled {
                background-color: #95a5a6;
                cursor: not-allowed;
            }