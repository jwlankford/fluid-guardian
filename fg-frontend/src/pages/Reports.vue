<script setup>
import { ref, computed, watch, onMounted, inject } from "vue";
import PeriodIntakeChart from "../components/PeriodIntakeChart.vue";
import { useAuth } from "../composables/useAuth.js";
import api from "../services/api.js";
import { generateReportPDF } from "../utils/pdfGenerator.js";

const showAlert = inject("showAlert");
const measurementSystem = inject("measurementSystem", ref("oz"));
const fluidLimit = inject("fluidLimit", ref(64));
const { userProfile } = useAuth();

// Helper to format Date to YYYY-MM-DD
const toISODate = (d) => {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

// Date range filters
const fromDate = ref("");
const toDate = ref("");
const activePreset = ref("all");

// Report state
const reportData = ref(null);
const isLoading = ref(false);

const unit = computed(() => (measurementSystem.value === "ml" ? "mL" : "oz"));

const getUserId = () => {
  return userProfile.value?.uid || "default_user";
};

// Quick date range presets
const setPreset = (preset) => {
  activePreset.value = preset;
  if (preset === "all") {
    fromDate.value = "";
    toDate.value = "";
    fetchReport(true);
    return;
  }

  const end = new Date();
  toDate.value = toISODate(end);

  if (preset === "month") {
    const start = new Date(end.getFullYear(), end.getMonth(), 1);
    fromDate.value = toISODate(start);
  } else {
    const days = Number(preset);
    const start = new Date();
    start.setDate(end.getDate() - (days - 1));
    fromDate.value = toISODate(start);
  }
  fetchReport(false);
};

// Generate fallback days when offline / mock
const generateFallbackDays = (startStr, endStr) => {
  const result = [];
  const start = new Date(startStr || new Date());
  const end = new Date(endStr || new Date());
  if (isNaN(start.getTime()) || isNaN(end.getTime()) || start > end) return result;

  const curr = new Date(start);
  while (curr <= end) {
    result.push({
      date: toISODate(curr),
      intake_ml: 0,
      running_intake_ml: 0,
      event_count: 0,
      events: [],
    });
    curr.setDate(curr.getDate() + 1);
  }
  return result;
};

// Fetch Report directly from database
const fetchReport = async (isAll = false) => {
  isLoading.value = true;
  const uid = getUserId();

  const params = {};
  if (!isAll && fromDate.value && toDate.value) {
    params.start_date = fromDate.value;
    params.end_date = toDate.value;
  }

  try {
    const res = await api.reporting.get(`/report/period/${uid}`, { params });
    reportData.value = res.data;
    if (res.data.start_date) {
      fromDate.value = res.data.start_date;
    }
    if (res.data.end_date) {
      toDate.value = res.data.end_date;
    }
  } catch (err) {
    console.warn("Could not fetch report from reporting backend:", err);
    // Attempt local fallback: fetch today's data from intake service or generate empty range
    try {
      const todayRes = await api.intake.get(`/intake/${uid}/today`);
      const todayData = todayRes.data;
      const todayStr = toISODate(new Date());
      const totalMl = todayData.total_fluid_ml || 0;
      reportData.value = {
        user_id: uid,
        start_date: todayStr,
        end_date: todayStr,
        total_intake_ml: totalMl,
        average_daily_ml: totalMl,
        event_count: todayData.event_count || 0,
        daily_totals_ml: { [todayStr]: totalMl },
        running_totals_ml: { [todayStr]: totalMl },
        days: [
          {
            date: todayStr,
            intake_ml: totalMl,
            running_intake_ml: totalMl,
            event_count: todayData.event_count || 0,
            events: todayData.events || [],
          },
        ],
      };
      fromDate.value = todayStr;
      toDate.value = todayStr;
    } catch {
      const todayStr = toISODate(new Date());
      reportData.value = {
        user_id: uid,
        start_date: fromDate.value || todayStr,
        end_date: toDate.value || todayStr,
        total_intake_ml: 0,
        average_daily_ml: 0,
        event_count: 0,
        daily_totals_ml: {},
        running_totals_ml: {},
        days: generateFallbackDays(fromDate.value || todayStr, toDate.value || todayStr),
      };
    }
  } finally {
    isLoading.value = false;
  }
};

const onCustomDateChange = () => {
  activePreset.value = "custom";
  if (fromDate.value && toDate.value) {
    fetchReport(false);
  }
};

watch(userProfile, () => {
  fetchReport(activePreset.value === "all");
});

onMounted(() => {
  fetchReport(true);
});

// Export & Email State
const isExportingPDF = ref(false);
const isEmailModalOpen = ref(false);
const isSendingEmail = ref(false);
const recipientEmail = ref("");
const emailSubject = ref("");
const emailMessage = ref("");

// CSV Export Handler (Excel)
const exportCSV = () => {
  const currentUnit = unit.value;
  const limitVal =
    measurementSystem.value === "ml"
      ? Math.round(fluidLimit.value * 29.5735)
      : fluidLimit.value;

  const startStr = fromDate.value || reportData.value?.start_date || "all";
  const endStr = toDate.value || reportData.value?.end_date || "all";
  const filename = `fluid_intake_report_${startStr}_to_${endStr}.csv`;
  let csvContent = `Date,Daily Intake (${currentUnit}),Running Total (${currentUnit}),Daily Limit (${currentUnit}),Limit Difference (${currentUnit}),Status,Events Count\n`;

  const daysList = reportData.value?.days || [];
  daysList.forEach((d) => {
    const dailyVal =
      measurementSystem.value === "ml"
        ? Math.round(d.intake_ml)
        : Math.round(d.intake_ml / 29.5735);
    const runningVal =
      measurementSystem.value === "ml"
        ? Math.round(d.running_intake_ml)
        : Math.round(d.running_intake_ml / 29.5735);
    const diff = dailyVal - limitVal;
    const status = diff > 0 ? "Over Limit" : "Within Limit";

    csvContent += `${d.date},${dailyVal},${runningVal},${limitVal},${diff},${status},${d.event_count || 0}\n`;
  });

  const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  if (showAlert) {
    showAlert(`CSV report downloaded: ${filename}`, "success");
  }
};

// PDF Export Handler
const exportPDF = async () => {
  if (isExportingPDF.value) return;
  isExportingPDF.value = true;
  if (showAlert) {
    showAlert("Generating PDF report... Download will start shortly.", "info");
  }

  try {
    const pdf = await generateReportPDF({
      reportData: reportData.value,
      userProfile: userProfile.value,
      measurementSystem: measurementSystem.value,
      fluidLimit: fluidLimit.value,
      startDate: fromDate.value,
      endDate: toDate.value,
    });

    pdf.save();
    if (showAlert) {
      showAlert(`PDF report downloaded: ${pdf.filename}`, "success");
    }
  } catch (err) {
    console.error("PDF generation failed:", err);
    if (showAlert) {
      showAlert("Could not generate PDF report. Please try again.", "error");
    }
  } finally {
    isExportingPDF.value = false;
  }
};

// Email Modal Handlers
const openEmailModal = () => {
  const patientName = userProfile.value?.name || userProfile.value?.firstName || "Patient";
  const startStr = fromDate.value || reportData.value?.start_date || "Start";
  const endStr = toDate.value || reportData.value?.end_date || "Present";
  const currentUnit = unit.value;
  const limitVal =
    measurementSystem.value === "ml"
      ? Math.round(fluidLimit.value * 29.5735)
      : fluidLimit.value;

  const daysList = reportData.value?.days || [];
  const totalMl = reportData.value?.total_intake_ml ?? (daysList.reduce((acc, d) => acc + (d.intake_ml || 0), 0));
  const totalVal = measurementSystem.value === "ml" ? Math.round(totalMl) : Math.round(totalMl / 29.5735);
  const avgVal = daysList.length > 0 ? Math.round(totalVal / daysList.length) : totalVal;

  let overLimitCount = 0;
  daysList.forEach((d) => {
    const dVal = measurementSystem.value === "ml" ? Math.round(d.intake_ml) : Math.round(d.intake_ml / 29.5735);
    if (dVal > limitVal) overLimitCount++;
  });

  recipientEmail.value = userProfile.value?.email || "";
  emailSubject.value = `Fluid Intake Report: ${patientName} (${startStr} to ${endStr})`;
  emailMessage.value = `Hello,\n\nPlease find attached the clinical fluid intake and compliance report for ${patientName}.\n\n` +
    `• Period: ${startStr} to ${endStr} (${daysList.length} days)\n` +
    `• Total Intake: ${totalVal} ${currentUnit}\n` +
    `• Daily Average: ${avgVal} ${currentUnit}/day\n` +
    `• Prescribed Limit: ${limitVal} ${currentUnit}/day\n` +
    `• Compliance: ${overLimitCount > 0 ? `${overLimitCount} day(s) over limit` : "100% within fluid limit"}\n\n` +
    `Generated via Fluid Guardian.`;

  isEmailModalOpen.value = true;
};

const closeEmailModal = () => {
  isEmailModalOpen.value = false;
  isSendingEmail.value = false;
};

// Send Email via Web Share API or native mail client
const sendEmailViaApp = async () => {
  if (isSendingEmail.value) return;
  isSendingEmail.value = true;

  try {
    const pdf = await generateReportPDF({
      reportData: reportData.value,
      userProfile: userProfile.value,
      measurementSystem: measurementSystem.value,
      fluidLimit: fluidLimit.value,
      startDate: fromDate.value,
      endDate: toDate.value,
    });

    const file = pdf.getFile();

    // Check if Web Share API with files is supported
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      await navigator.share({
        title: emailSubject.value,
        text: emailMessage.value,
        files: [file],
      });
      if (showAlert) showAlert("Report shared successfully via mail!", "success");
      closeEmailModal();
    } else {
      // Fallback: auto-download PDF and launch mailto:
      pdf.save();
      const mailtoUrl = `mailto:${encodeURIComponent(recipientEmail.value)}?subject=${encodeURIComponent(
        emailSubject.value
      )}&body=${encodeURIComponent(emailMessage.value)}`;
      window.location.href = mailtoUrl;

      if (showAlert) {
        showAlert("Email opened! The PDF has also been downloaded to your device to attach.", "success");
      }
      closeEmailModal();
    }
  } catch (err) {
    if (err.name !== "AbortError") {
      console.error("Error sharing email:", err);
      if (showAlert) showAlert("Could not open mail app. Please try sending via server.", "error");
    }
  } finally {
    isSendingEmail.value = false;
  }
};

// Send Email via Backend Service
const sendEmailViaServer = async () => {
  if (isSendingEmail.value) return;
  if (!recipientEmail.value || !recipientEmail.value.includes("@")) {
    if (showAlert) showAlert("Please enter a valid recipient email address.", "error");
    return;
  }

  isSendingEmail.value = true;
  try {
    const pdf = await generateReportPDF({
      reportData: reportData.value,
      userProfile: userProfile.value,
      measurementSystem: measurementSystem.value,
      fluidLimit: fluidLimit.value,
      startDate: fromDate.value,
      endDate: toDate.value,
    });

    const payload = {
      user_id: getUserId(),
      to_email: recipientEmail.value.trim(),
      subject: emailSubject.value,
      body: emailMessage.value,
      pdf_base64: pdf.getBase64(),
      filename: pdf.filename,
    };

    const res = await api.reporting.post("/report/send-email", payload);
    const msg = res.data?.message || `Report successfully emailed to ${recipientEmail.value}`;
    if (showAlert) showAlert(msg, "success");
    closeEmailModal();
  } catch (err) {
    console.error("Failed to send email via reporting service:", err);
    if (showAlert) {
      showAlert("Server send encountered an issue. Opening your mail app instead...", "warning");
    }
    await sendEmailViaApp();
  } finally {
    isSendingEmail.value = false;
  }
};

const handleExport = (type) => {
  if (type === "CSV") {
    exportCSV();
  } else if (type === "Email") {
    openEmailModal();
  } else if (type === "PDF") {
    exportPDF();
  }
};
</script>

<template>
  <section class="reports-page">
    <h1 class="page-title">Reports</h1>

    <!-- Report Controls (Date Range & Presets) -->
    <div class="report-controls card">
      <div class="period-controls-wrapper">
        <div class="date-pickers period-pickers">
          <div class="custom-input-group">
            <label>From</label>
            <input
              type="date"
              v-model="fromDate"
              :max="toDate"
              @change="onCustomDateChange"
            />
          </div>
          <div class="custom-input-group">
            <label>To</label>
            <input
              type="date"
              v-model="toDate"
              :min="fromDate"
              @change="onCustomDateChange"
            />
          </div>
        </div>

        <!-- Quick Preset Pills -->
        <div class="preset-pills">
          <button
            type="button"
            :class="['preset-pill', { active: activePreset === 'all' }]"
            @click="setPreset('all')"
          >
            All Data
          </button>
          <button
            type="button"
            :class="['preset-pill', { active: activePreset === 7 }]"
            @click="setPreset(7)"
          >
            7 Days
          </button>
          <button
            type="button"
            :class="['preset-pill', { active: activePreset === 14 }]"
            @click="setPreset(14)"
          >
            14 Days
          </button>
          <button
            type="button"
            :class="['preset-pill', { active: activePreset === 30 }]"
            @click="setPreset(30)"
          >
            30 Days
          </button>
          <button
            type="button"
            :class="['preset-pill', { active: activePreset === 'month' }]"
            @click="setPreset('month')"
          >
            This Month
          </button>
        </div>
      </div>
    </div>

    <!-- Fluid Intake Chart & Day Details -->
    <PeriodIntakeChart
      :days="reportData?.days || []"
      :fluid-limit="fluidLimit"
      :measurement-system="measurementSystem"
      :is-loading="isLoading"
      :start-date="fromDate"
      :end-date="toDate"
    />

    <!-- Export Action Buttons -->
    <div class="report-actions">
      <button
        class="action-btn email-btn"
        title="Email PDF Report"
        @click="handleExport('Email')"
        :disabled="isExportingPDF || isLoading"
      >
        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
      </button>

      <button
        class="action-btn pdf-btn"
        title="Download PDF"
        @click="handleExport('PDF')"
        :disabled="isExportingPDF || isLoading"
      >
        <span v-if="isExportingPDF" class="btn-spinner"></span>
        <svg v-else width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
      </button>

      <button
        class="action-btn excel-btn"
        title="Download CSV (Excel)"
        @click="handleExport('CSV')"
        :disabled="isLoading"
      >
        <!-- Excel Spreadsheet Icon -->
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="8" y1="13" x2="16" y2="13" />
          <line x1="8" y1="17" x2="16" y2="17" />
          <line x1="10" y1="9" x2="10" y2="21" />
        </svg>
      </button>
    </div>

    <!-- Email PDF Report Modal -->
    <div v-if="isEmailModalOpen" class="email-modal-overlay" @click.self="closeEmailModal">
      <div class="email-modal-card card">
        <div class="modal-header">
          <div class="modal-title-wrap">
            <div class="modal-icon-badge">
              <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <h2 class="modal-title">Email Fluid Report</h2>
              <p class="modal-subtitle">Send clinical PDF report to clinician or patient</p>
            </div>
          </div>
          <button class="modal-close-btn" @click="closeEmailModal" aria-label="Close">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <!-- Attachment Chip -->
          <div class="pdf-attachment-chip">
            <div class="chip-file-info">
              <svg class="chip-pdf-icon" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <div class="chip-text">
                <span class="chip-filename">Fluid_Guardian_Report_{{ fromDate || 'all' }}_to_{{ toDate || 'all' }}.pdf</span>
                <span class="chip-meta">Clinical PDF Document • Chart & Table</span>
              </div>
            </div>
            <button type="button" class="chip-download-btn" @click="exportPDF" title="Download copy to your device">
              Download PDF
            </button>
          </div>

          <!-- Form Fields -->
          <div class="modal-form-group">
            <label for="modal-recipient-email">Recipient Email</label>
            <input
              id="modal-recipient-email"
              type="email"
              v-model="recipientEmail"
              placeholder="e.g. doctor@hospital.org"
              required
            />
          </div>

          <div class="modal-form-group">
            <label for="modal-subject">Subject</label>
            <input
              id="modal-subject"
              type="text"
              v-model="emailSubject"
            />
          </div>

          <div class="modal-form-group">
            <label for="modal-message">Clinical Notes / Message</label>
            <textarea
              id="modal-message"
              rows="4"
              v-model="emailMessage"
            ></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeEmailModal" :disabled="isSendingEmail">
            Cancel
          </button>
          <div class="primary-actions-group">
            <button
              type="button"
              class="btn-send btn-send-server"
              @click="sendEmailViaServer"
              :disabled="isSendingEmail"
              title="Send directly from Fluid Guardian reporting service"
            >
              <span v-if="isSendingEmail" class="btn-spinner"></span>
              <svg v-else width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
              <span>{{ isSendingEmail ? 'Sending...' : 'Send via Server' }}</span>
            </button>
            <button
              type="button"
              class="btn-send btn-send-app"
              @click="sendEmailViaApp"
              :disabled="isSendingEmail"
              title="Open native email client or share with PDF attached"
            >
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
              </svg>
              <span>Open Mail App</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.reports-page {
  padding: 1rem;
  padding-bottom: 5rem;
  max-width: 600px;
  margin: 0 auto;
}

.page-title {
  color: #007BFF;
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0 0 1.25rem 0;
}

.report-controls {
  padding: 16px;
  margin-bottom: 16px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  border: 1px solid #e2e8f0;
}

.period-controls-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.date-pickers {
  display: flex;
  gap: 12px;
}

.custom-input-group {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 4px;
}

.custom-input-group label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.custom-input-group input {
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #333333;
  background: #ffffff;
  transition: border-color 0.2s;
  width: 100%;
}

.custom-input-group input:focus {
  outline: none;
  border-color: #007BFF;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
}

/* Preset pills */
.preset-pills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.preset-pill {
  padding: 4px 10px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-pill:hover {
  background: #e2e8f0;
  color: #0f172a;
  border-color: #cbd5e1;
}

.preset-pill.active {
  background: #007BFF;
  color: #ffffff;
  border-color: #007BFF;
}

/* Action Buttons */
.report-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 50%;
  color: #007BFF;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.action-btn:hover:not(:disabled) {
  background: #f8fafc;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

/* Custom button hover accents */
.email-btn:hover:not(:disabled) {
  border-color: #007BFF;
  color: #007BFF;
}

.pdf-btn:hover:not(:disabled) {
  border-color: #ef4444;
  color: #ef4444;
}

.excel-btn:hover:not(:disabled) {
  border-color: #107C41;
  color: #107C41;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e2e8f0;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Email Modal Overlay */
.email-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.email-modal-card {
  width: 100%;
  max-width: 520px;
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.modal-title-wrap {
  display: flex;
  gap: 12px;
  align-items: center;
}

.modal-icon-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  background: #eff6ff;
  color: #007BFF;
  border-radius: 10px;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.8rem;
  color: #64748b;
  margin: 2px 0 0 0;
}

.modal-close-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close-btn:hover {
  background: #f1f5f9;
  color: #334155;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.pdf-attachment-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  gap: 10px;
}

.chip-file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow: hidden;
}

.chip-pdf-icon {
  color: #ef4444;
  flex-shrink: 0;
}

.chip-text {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chip-filename {
  font-size: 0.8rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chip-meta {
  font-size: 0.7rem;
  color: #64748b;
}

.chip-download-btn {
  background: transparent;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.72rem;
  font-weight: 600;
  color: #007BFF;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.chip-download-btn:hover {
  background: #eff6ff;
  border-color: #93c5fd;
}

.modal-form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.modal-form-group label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
}

.modal-form-group input,
.modal-form-group textarea {
  padding: 9px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #1e293b;
  background: #ffffff;
  font-family: inherit;
  transition: border-color 0.2s;
}

.modal-form-group input:focus,
.modal-form-group textarea:focus {
  outline: none;
  border-color: #007BFF;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.primary-actions-group {
  display: flex;
  gap: 8px;
}

.btn-cancel {
  padding: 8px 14px;
  background: transparent;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover:not(:disabled) {
  background: #f1f5f9;
  color: #334155;
}

.btn-send {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-send:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-send-server {
  background: #007BFF;
  color: #ffffff;
}

.btn-send-server:hover:not(:disabled) {
  background: #0066d6;
}

.btn-send-app {
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #cbd5e1;
}

.btn-send-app:hover:not(:disabled) {
  background: #e2e8f0;
  color: #0f172a;
}

/* Dark mode overrides */
html.dark .action-btn {
  background: #141414;
  border-color: #333333;
  color: #00CFFF;
}

html.dark .action-btn:hover:not(:disabled) {
  background: #222222;
}

html.dark .email-btn:hover:not(:disabled) {
  border-color: #00CFFF;
  color: #00CFFF;
}

html.dark .pdf-btn:hover:not(:disabled) {
  border-color: #f87171;
  color: #f87171;
}

html.dark .excel-btn:hover:not(:disabled) {
  border-color: #4ade80;
  color: #4ade80;
}

html.dark .report-controls {
  background: #141414;
  border-color: #333333;
}

html.dark .custom-input-group label {
  color: #94a3b8;
}

html.dark .custom-input-group input {
  background: #1e1e1e;
  border-color: #333333;
  color: #f8fafc;
}

html.dark .custom-input-group input:focus {
  border-color: #00CFFF;
  box-shadow: 0 0 0 2px rgba(0, 207, 255, 0.2);
}

html.dark .preset-pill {
  background: #222222;
  border-color: #333333;
  color: #94a3b8;
}

html.dark .preset-pill:hover {
  background: #333333;
  color: #f8fafc;
  border-color: #444444;
}

html.dark .preset-pill.active {
  background: #00CFFF;
  color: #000000;
  border-color: #00CFFF;
}

/* Dark mode for email modal */
html.dark .email-modal-card {
  background: #141414;
  border-color: #333333;
}

html.dark .modal-title {
  color: #f8fafc;
}

html.dark .modal-subtitle {
  color: #94a3b8;
}

html.dark .modal-icon-badge {
  background: #1e293b;
  color: #00CFFF;
}

html.dark .modal-close-btn:hover {
  background: #222222;
  color: #f8fafc;
}

html.dark .pdf-attachment-chip {
  background: #1e1e1e;
  border-color: #333333;
}

html.dark .chip-filename {
  color: #f8fafc;
}

html.dark .chip-meta {
  color: #94a3b8;
}

html.dark .chip-download-btn {
  border-color: #444444;
  color: #00CFFF;
}

html.dark .chip-download-btn:hover {
  background: #1e293b;
}

html.dark .modal-form-group label {
  color: #cbd5e1;
}

html.dark .modal-form-group input,
html.dark .modal-form-group textarea {
  background: #1e1e1e;
  border-color: #333333;
  color: #f8fafc;
}

html.dark .modal-form-group input:focus,
html.dark .modal-form-group textarea:focus {
  border-color: #00CFFF;
  box-shadow: 0 0 0 2px rgba(0, 207, 255, 0.2);
}

html.dark .btn-cancel {
  border-color: #333333;
  color: #94a3b8;
}

html.dark .btn-cancel:hover:not(:disabled) {
  background: #222222;
  color: #f8fafc;
}

html.dark .btn-send-server {
  background: #00CFFF;
  color: #000000;
}

html.dark .btn-send-server:hover:not(:disabled) {
  background: #38bdf8;
}

html.dark .btn-send-app {
  background: #222222;
  border-color: #333333;
  color: #f8fafc;
}

html.dark .btn-send-app:hover:not(:disabled) {
  background: #333333;
}
</style>
