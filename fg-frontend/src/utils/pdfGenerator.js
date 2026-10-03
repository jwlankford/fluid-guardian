import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import html2canvas from "html2canvas";

/**
 * Generates a professional clinical PDF report for Fluid Guardian.
 *
 * @param {Object} options
 * @param {Object} options.reportData - The period report data object
 * @param {Object} [options.userProfile] - User auth profile (name, email, uid)
 * @param {string} [options.measurementSystem='oz'] - 'oz' or 'ml'
 * @param {number} [options.fluidLimit=64] - Prescribed daily limit (oz)
 * @param {string} [options.startDate=''] - Start date (YYYY-MM-DD)
 * @param {string} [options.endDate=''] - End date (YYYY-MM-DD)
 * @param {HTMLElement|null} [options.chartElement=null] - DOM element for chart snapshot
 * @returns {Promise<{ doc: jsPDF, filename: string, save: Function, getBlob: Function, getFile: Function, getBase64: Function }>}
 */
export async function generateReportPDF({
  reportData,
  userProfile = {},
  measurementSystem = "oz",
  fluidLimit = 64,
  startDate = "",
  endDate = "",
  chartElement = null,
}) {
  const isMl = measurementSystem.toLowerCase() === "ml";
  const unit = isMl ? "mL" : "oz";
  const limitVal = isMl ? Math.round(fluidLimit * 29.5735) : fluidLimit;

  const days = reportData?.days || [];
  const startStr = startDate || reportData?.start_date || (days[0]?.date ?? "Start");
  const endStr = endDate || reportData?.end_date || (days[days.length - 1]?.date ?? "End");
  const filename = `Fluid_Guardian_Report_${startStr}_to_${endStr}.pdf`;

  // Aggregate metrics
  const totalMl = reportData?.total_intake_ml ?? (days.reduce((acc, d) => acc + (d.intake_ml || 0), 0));
  const totalVal = isMl ? Math.round(totalMl) : Math.round(totalMl / 29.5735);
  const avgVal = days.length > 0 ? Math.round(totalVal / days.length) : totalVal;

  let overLimitCount = 0;
  days.forEach((d) => {
    const dVal = isMl ? Math.round(d.intake_ml) : Math.round(d.intake_ml / 29.5735);
    if (dVal > limitVal) overLimitCount++;
  });

  const patientName = userProfile?.name || userProfile?.firstName || "Fluid Guardian User";
  const patientEmail = userProfile?.email || "N/A";
  const generatedAt = new Date().toLocaleString("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  });

  // Create Letter size PDF (612 x 792 pt)
  const doc = new jsPDF({
    orientation: "portrait",
    unit: "pt",
    format: "letter",
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 36;
  const contentWidth = pageWidth - margin * 2;

  // 1. Header Banner
  doc.setFillColor(0, 123, 255); // Fluid Guardian Primary Blue
  doc.roundedRect(margin, margin, contentWidth, 54, 6, 6, "F");

  doc.setTextColor(255, 255, 255);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.text("FLUID GUARDIAN", margin + 14, margin + 24);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(220, 235, 255);
  doc.text("CLINICAL FLUID INTAKE & COMPLIANCE REPORT", margin + 14, margin + 40);

  doc.setFontSize(8);
  doc.setTextColor(255, 255, 255);
  doc.text(`Generated: ${generatedAt}`, pageWidth - margin - 14, margin + 32, { align: "right" });

  // 2. Patient & Report Metadata Box
  let currentY = margin + 64;
  doc.setFillColor(248, 250, 252);
  doc.setDrawColor(226, 232, 240);
  doc.setLineWidth(0.75);
  doc.roundedRect(margin, currentY, contentWidth, 48, 4, 4, "FD");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(8.5);
  doc.setTextColor(100, 116, 139);
  doc.text("PATIENT INFORMATION", margin + 12, currentY + 14);
  doc.text("REPORT PARAMETERS", margin + contentWidth / 2 + 10, currentY + 14);

  doc.setFont("helvetica", "normal");
  doc.setTextColor(15, 23, 42);
  doc.setFontSize(9);
  doc.text(`Name: ${patientName}`, margin + 12, currentY + 28);
  doc.text(`Email: ${patientEmail}`, margin + 12, currentY + 40);

  doc.text(`Date Range: ${startStr} to ${endStr} (${days.length} days)`, margin + contentWidth / 2 + 10, currentY + 28);
  doc.text(`Prescribed Limit: ${limitVal} ${unit}/day`, margin + contentWidth / 2 + 10, currentY + 40);

  // 3. Summary Metric Cards
  currentY += 56;
  const cardWidth = (contentWidth - 18) / 4;
  const cardHeight = 44;

  const metrics = [
    { label: "TOTAL INTAKE", val: `${totalVal} ${unit}`, color: [0, 123, 255] },
    { label: "DAILY AVERAGE", val: `${avgVal} ${unit}/d`, color: [15, 23, 42] },
    { label: "DAILY LIMIT", val: `${limitVal} ${unit}`, color: [100, 116, 139] },
    {
      label: "COMPLIANCE STATUS",
      val: overLimitCount > 0 ? `${overLimitCount}d Over Limit` : "Within Limit",
      color: overLimitCount > 0 ? [220, 38, 38] : [22, 163, 74],
    },
  ];

  metrics.forEach((m, idx) => {
    const cardX = margin + idx * (cardWidth + 6);
    doc.setFillColor(248, 250, 252);
    doc.setDrawColor(226, 232, 240);
    doc.roundedRect(cardX, currentY, cardWidth, cardHeight, 4, 4, "FD");

    doc.setFont("helvetica", "bold");
    doc.setFontSize(6.5);
    doc.setTextColor(100, 116, 139);
    doc.text(m.label, cardX + cardWidth / 2, currentY + 13, { align: "center" });

    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(m.color[0], m.color[1], m.color[2]);
    doc.text(m.val, cardX + cardWidth / 2, currentY + 31, { align: "center" });
  });

  currentY += cardHeight + 14;

  // 4. Capture & Embed SVG Chart Snapshot
  try {
    const targetChart = chartElement || document.querySelector(".period-chart-container") || document.querySelector(".svg-wrapper");
    if (targetChart) {
      const canvas = await html2canvas(targetChart, {
        scale: 2,
        backgroundColor: "#ffffff",
        logging: false,
        useCORS: true,
      });

      const imgData = canvas.toDataURL("image/png");
      const imgWidth = contentWidth;
      const imgHeight = Math.min((canvas.height * imgWidth) / canvas.width, 180);

      // Section label
      doc.setFont("helvetica", "bold");
      doc.setFontSize(9.5);
      doc.setTextColor(15, 23, 42);
      doc.text("FLUID INTAKE VISUAL TREND", margin, currentY + 8);
      currentY += 14;

      doc.setDrawColor(226, 232, 240);
      doc.setLineWidth(0.5);
      doc.addImage(imgData, "PNG", margin, currentY, imgWidth, imgHeight, undefined, "FAST");
      currentY += imgHeight + 16;
    }
  } catch (err) {
    console.warn("Chart image could not be embedded in PDF:", err);
  }

  // 5. Daily Breakdown Table
  doc.setFont("helvetica", "bold");
  doc.setFontSize(9.5);
  doc.setTextColor(15, 23, 42);
  doc.text("DAILY BREAKDOWN LOG", margin, currentY + 8);
  currentY += 12;

  const tableHead = [
    [
      "Date",
      `Intake (${unit})`,
      `Running (${unit})`,
      `Limit (${unit})`,
      `Diff (${unit})`,
      "Status",
      "Events",
    ],
  ];

  const tableBody = days.map((d) => {
    const dailyVal = isMl ? Math.round(d.intake_ml) : Math.round(d.intake_ml / 29.5735);
    const runningVal = isMl ? Math.round(d.running_intake_ml) : Math.round(d.running_intake_ml / 29.5735);
    const diff = dailyVal - limitVal;
    const isOver = diff > 0;
    const diffStr = diff > 0 ? `+${diff}` : `${diff}`;
    const statusStr = isOver ? "Over Limit" : "Within Limit";
    const evCount = d.event_count || (d.events ? d.events.length : 0);

    return [
      d.date,
      dailyVal.toString(),
      runningVal.toString(),
      limitVal.toString(),
      diffStr,
      statusStr,
      `${evCount} log${evCount === 1 ? "" : "s"}`,
    ];
  });

  autoTable(doc, {
    startY: currentY,
    head: tableHead,
    body: tableBody,
    margin: { left: margin, right: margin, bottom: 40 },
    theme: "striped",
    headStyles: {
      fillColor: [0, 123, 255],
      textColor: 255,
      fontStyle: "bold",
      fontSize: 8,
      halign: "center",
      cellPadding: 4,
    },
    bodyStyles: {
      fontSize: 7.5,
      halign: "center",
      cellPadding: 3.5,
      textColor: [30, 41, 59],
    },
    alternateRowStyles: {
      fillColor: [248, 250, 252],
    },
    columnStyles: {
      0: { halign: "left", fontStyle: "bold" },
      1: { halign: "right" },
      2: { halign: "right" },
      3: { halign: "right" },
      4: { halign: "right", fontStyle: "bold" },
      5: { halign: "center", fontStyle: "bold" },
      6: { halign: "center" },
    },
    didParseCell: (data) => {
      if (data.section === "body") {
        const row = days[data.row.index];
        if (row) {
          const dailyVal = isMl ? Math.round(row.intake_ml) : Math.round(row.intake_ml / 29.5735);
          const isOver = dailyVal > limitVal;

          if (data.column.index === 4 || data.column.index === 5) {
            if (isOver) {
              data.cell.styles.textColor = [220, 38, 38]; // Red
              data.cell.styles.fillColor = [254, 242, 242]; // Light red
            } else {
              data.cell.styles.textColor = [22, 163, 74]; // Green
            }
          }
        }
      }
    },
  });

  // 6. Footer on all pages
  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setDrawColor(226, 232, 240);
    doc.setLineWidth(0.5);
    doc.line(margin, pageHeight - 28, pageWidth - margin, pageHeight - 28);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(7.5);
    doc.setTextColor(148, 163, 184);
    doc.text(
      "Fluid Guardian • Clinical Fluid Management & Compliance Tracking Record",
      margin,
      pageHeight - 16
    );
    doc.text(
      `Page ${i} of ${totalPages}`,
      pageWidth - margin,
      pageHeight - 16,
      { align: "right" }
    );
  }

  return {
    doc,
    filename,
    save: (customName) => doc.save(customName || filename),
    getBlob: () => doc.output("blob"),
    getFile: (customName) =>
      new File([doc.output("blob")], customName || filename, {
        type: "application/pdf",
      }),
    getBase64: () => {
      const dataUri = doc.output("datauristring");
      const parts = dataUri.split(",");
      return parts.length > 1 ? parts[1] : parts[0];
    },
  };
}
