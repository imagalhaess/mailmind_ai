// MailMind - Frontend JavaScript
class EmailAnalyzer {
  constructor() {
    this.currentTab = "analyze";
    this.selectedFile = null; // Armazena o arquivo selecionado
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupFileUpload();
    this.setupTabs();
  }

  setupEventListeners() {
    // Tab navigation
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const tab = item.dataset.tab;
        this.switchTab(tab);
      });
    });

    // Input type radio buttons
    document.querySelectorAll('input[name="inputType"]').forEach((radio) => {
      radio.addEventListener("change", (e) => {
        this.toggleInputType(e.target.value);
      });
    });

    // Analyze button
    document.getElementById("analyzeBtn").addEventListener("click", () => {
      this.handleAnalyze();
    });

    // Test buttons
    document.getElementById("testSpamBtn").addEventListener("click", () => {
      this.handleTest("improdutivo");
    });

    document
      .getElementById("testProductiveBtn")
      .addEventListener("click", () => {
        this.handleTest("produtivo");
      });

    // Webhook button
    document.getElementById("webhookBtn").addEventListener("click", () => {
      this.handleWebhook();
    });

    // Webhook test button
    document.getElementById("webhookTestBtn").addEventListener("click", () => {
      this.loadTestWebhookData();
    });

    // Test tab buttons
    document
      .getElementById("testImprodutivoBtn")
      .addEventListener("click", () => {
        this.handleTest("improdutivo");
      });

    document
      .getElementById("testProdutivoBtn")
      .addEventListener("click", () => {
        this.handleTest("produtivo");
      });
  }

  setupFileUpload() {
    const fileUpload = document.getElementById("fileUpload");
    const fileInput = document.getElementById("fileInput");
    const fileInfo = document.getElementById("fileInfo");
    const selectFileBtn = document.getElementById("selectFileBtn");

    // Drag and drop
    fileUpload.addEventListener("dragover", (e) => {
      e.preventDefault();
      fileUpload.classList.add("dragging");
    });

    fileUpload.addEventListener("dragleave", () => {
      fileUpload.classList.remove("dragging");
    });

    fileUpload.addEventListener("drop", (e) => {
      e.preventDefault();
      fileUpload.classList.remove("dragging");

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.handleFileSelect(files[0]);
      }
    });

    // File input change
    fileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        this.handleFileSelect(e.target.files[0]);
      }
    });

    // Click to select file - apenas na área de drop, não no botão
    fileUpload.addEventListener("click", (e) => {
      // Evita conflito com o botão
      if (
        e.target === fileUpload ||
        e.target.classList.contains("file-text") ||
        e.target.classList.contains("file-hint")
      ) {
        fileInput.click();
      }
    });

    // Botão separado para seleção
    selectFileBtn.addEventListener("click", (e) => {
      e.stopPropagation(); // Evita propagação para o fileUpload
      fileInput.click();
    });
  }

  setupTabs() {
    // Initialize with analyze tab active
    this.switchTab("analyze");
  }

  switchTab(tabName) {
    // Update navigation
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.classList.remove("active");
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add("active");

    // Update tab content
    document.querySelectorAll(".tab-content").forEach((content) => {
      content.classList.remove("active");
    });
    document.getElementById(`${tabName}-tab`).classList.add("active");

    this.currentTab = tabName;
  }

  toggleInputType(type) {
    const textInput = document.getElementById("text-input");
    const fileInput = document.getElementById("file-input");

    if (type === "text") {
      textInput.style.display = "block";
      fileInput.style.display = "none";
    } else {
      textInput.style.display = "none";
      fileInput.style.display = "block";
    }
  }

  handleFileSelect(file) {
    const allowedTypes = ["text/plain", "application/pdf"];

    if (!allowedTypes.includes(file.type)) {
      this.showToast("Apenas arquivos .txt e .pdf são permitidos", "error");
      return;
    }

    // Armazena o arquivo selecionado para uso posterior
    this.selectedFile = file;

    const fileInfo = document.getElementById("fileInfo");
    fileInfo.innerHTML = `Arquivo selecionado: <strong>${file.name}</strong>`;
    fileInfo.style.display = "block";

    this.showToast(`Arquivo "${file.name}" selecionado`, "success");
  }

  async handleAnalyze() {
    const inputType = document.querySelector(
      'input[name="inputType"]:checked'
    ).value;
    const emailContent = document.getElementById("emailContent").value.trim();
    const senderEmail = document.getElementById("senderEmail").value.trim();

    // Validation
    if (inputType === "text" && !emailContent) {
      this.showToast("Por favor, insira o conteúdo do email", "error");
      return;
    }

    if (inputType === "file" && !this.selectedFile) {
      this.showToast("Por favor, selecione um arquivo", "error");
      return;
    }

    const analyzeBtn = document.getElementById("analyzeBtn");
    const analyzeText = document.getElementById("analyzeText");

    this.setLoading(analyzeBtn, analyzeText, "Analisando...");

    try {
      let result;

      if (inputType === "file") {
        result = await this.uploadFile(this.selectedFile);
      } else {
        result = await this.analyzeText(emailContent, senderEmail);
      }

      this.showResult(result);
      this.showToast("Email analisado com sucesso!", "success");
    } catch (error) {
      console.error("Erro na análise:", error);
      this.showToast(`Erro ao analisar email: ${error.message}`, "error");
    } finally {
      this.setLoading(analyzeBtn, analyzeText, "Analisar Email", false);
    }
  }

  async handleTest(testType) {
    const testBtn = document.querySelector(
      `#test${testType.charAt(0).toUpperCase() + testType.slice(1)}Btn`
    );
    const testText = testBtn.querySelector("span") || testBtn;

    this.setLoading(testBtn, testText, "Executando...");

    try {
      const result = await this.runTest(testType);
      this.showResult(result);
      this.showToast(`Teste de email ${testType} executado!`, "success");
    } catch (error) {
      console.error("Erro no teste:", error);
      this.showToast("Erro ao executar teste. Tente novamente.", "error");
    } finally {
      this.setLoading(testBtn, testText, "Executar Teste", false);
    }
  }

  loadTestWebhookData() {
    const testData = {
      sender: "teste@exemplo.com",
      subject: "Teste de Webhook",
      content: "Este é um email de teste enviado via webhook.",
    };

    const webhookData = document.getElementById("webhookData");
    webhookData.value = JSON.stringify(testData, null, 2);
    this.showToast("JSON de teste carregado!", "success");
  }

  async handleWebhook() {
    const webhookData = document.getElementById("webhookData").value.trim();
    const webhookBtn = document.getElementById("webhookBtn");
    const webhookText = document.getElementById("webhookText");

    if (!webhookData) {
      this.showToast("Por favor, insira os dados JSON", "error");
      return;
    }

    this.setLoading(webhookBtn, webhookText, "Enviando...");

    try {
      // Debug: mostrar o JSON que está sendo enviado
      console.log("JSON sendo enviado:", webhookData);

      const data = JSON.parse(webhookData);
      console.log("JSON parseado:", data);

      const result = await this.testWebhook(data);
      this.showResult(result);
      this.showToast("Dados enviados para webhook com sucesso!", "success");
    } catch (error) {
      console.error("Erro no webhook:", error);
      console.error("JSON problemático:", webhookData);

      if (error instanceof SyntaxError) {
        this.showToast(`JSON inválido: ${error.message}`, "error");
      } else {
        this.showToast(
          `Erro ao enviar dados para webhook: ${error.message}`,
          "error"
        );
      }
    } finally {
      this.setLoading(webhookBtn, webhookText, "Enviar para Webhook", false);
    }
  }

  async analyzeText(emailContent, senderEmail) {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email_content: emailContent,
        sender: senderEmail || undefined,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async uploadFile(file) {
    const formData = new FormData();
    formData.append("email_file", file); // Corrigido: usar 'email_file' como esperado pelo backend

    const response = await fetch("/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`
      );
    }

    return await response.json();
  }

  async runTest(testType) {
    const response = await fetch(`/test/${testType}`, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async testWebhook(data) {
    const response = await fetch("/webhook/email", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`
      );
    }

    return await response.json();
  }

  showResult(result) {
    const resultsSection = document.getElementById("results");
    const resultContent = document.getElementById("resultContent");

    // Handle webhook result (tem estrutura diferente)
    if (result.result && result.result.categoria) {
      resultContent.innerHTML = this.formatSingleResult(result.result);
    }
    // Handle single result (API retorna 'categoria' e 'atencao_humana')
    else if (result.categoria || result.atencao_humana) {
      resultContent.innerHTML = this.formatSingleResult(result);
    }
    // Handle batch results
    else if (result.results && Array.isArray(result.results)) {
      resultContent.innerHTML = this.formatBatchResults(result);
    }
    // Handle error
    else if (result.error) {
      resultContent.innerHTML = `
                <div class="result-item">
                    <div class="result-status destructive">Erro</div>
                    <div class="result-summary">${result.error}</div>
                </div>
            `;
    }
    // Handle other cases
    else {
      resultContent.innerHTML = `
                <div class="result-item">
                    <div class="result-status">Resultado</div>
                    <div class="result-summary">${JSON.stringify(
                      result,
                      null,
                      2
                    )}</div>
                </div>
            `;
    }

    resultsSection.style.display = "block";
    resultsSection.scrollIntoView({ behavior: "smooth" });
  }

  formatSingleResult(result) {
    // Determina se é produtivo baseado na atenção humana
    const isProdutivo = result.atencao_humana === "SIM";
    const statusClass = isProdutivo ? "produtivo" : "improdutivo";
    const statusText = isProdutivo ? "Produtivo" : "Improdutivo";

    return `
            <div class="result-item">
                <div class="result-status ${statusClass}">${statusText}</div>
                <div class="result-summary">
                    <strong>Categoria:</strong> ${result.categoria || "N/A"}
                </div>
                <div class="result-summary">
                    <strong>Resumo:</strong> ${result.resumo || "N/A"}
                </div>
                <div class="result-actions">
                    <strong>Sugestão:</strong> ${result.sugestao || "N/A"}
                </div>
                <div class="result-actions">
                    <strong>Ação Executada:</strong> ${
                      result.acao_executada || "N/A"
                    }
                </div>
            </div>
        `;
  }

  formatBatchResults(result) {
    // Conta emails produtivos (SIM) e improdutivos (NÃO)
    const produtivos = result.results.filter(
      (r) => r.atencao_humana === "SIM"
    ).length;
    const improdutivos = result.results.filter(
      (r) => r.atencao_humana === "NÃO"
    ).length;

    let html = `
            <div class="result-item">
                <div class="result-summary">
                    <strong>Total de emails processados:</strong> ${result.results.length}
                </div>
                <div class="result-actions">
                    <strong>Emails produtivos:</strong> ${produtivos}
                </div>
                <div class="result-actions">
                    <strong>Emails improdutivos:</strong> ${improdutivos}
                </div>
            </div>
        `;

    result.results.forEach((emailResult, index) => {
      html += this.formatSingleResult(emailResult);
    });

    return html;
  }

  setLoading(button, textElement, loadingText, isLoading = true) {
    if (isLoading) {
      button.disabled = true;
      textElement.innerHTML = `
                <div class="spinner"></div>
                ${loadingText}
            `;
    } else {
      button.disabled = false;
      textElement.innerHTML = loadingText;
    }
  }

  showToast(message, type = "success") {
    const toastContainer = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;

    toastContainer.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
      toast.remove();
    }, 5000);
  }
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new EmailAnalyzer();
});
