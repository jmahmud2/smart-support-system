import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

export const exportTicketsToCSV = (tickets, filename = 'tickets_export.csv') => {
  const data = tickets.map(t => ({
    'ID': t.id,
    'Customer Name': t.customer_name || 'Anonymous',
    'Customer Email': t.customer_email || '',
    'Message': t.customer_message?.substring(0, 200) || '',
    'Intent': t.intent || 'unknown',
    'Sentiment': t.sentiment || 'neutral',
    'Priority': t.priority || 'low',
    'Status': t.status || 'new',
    'Escalated': t.escalate ? 'Yes' : 'No',
    'Assigned To': t.assigned_to || 'Unassigned',
    'Created': new Date(t.created_at).toLocaleDateString(),
    'Resolved': t.resolved_at ? new Date(t.resolved_at).toLocaleDateString() : 'N/A',
    'Summary': t.ticket_summary || '',
  }));

  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Tickets');
  const wbout = XLSX.write(wb, { bookType: 'csv', type: 'array' });
  
  const blob = new Blob([wbout], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, filename);
};

export const exportTicketsToExcel = (tickets, filename = 'tickets_export.xlsx') => {
  const data = tickets.map(t => ({
    'ID': t.id,
    'Customer Name': t.customer_name || 'Anonymous',
    'Customer Email': t.customer_email || '',
    'Message': t.customer_message?.substring(0, 200) || '',
    'Intent': t.intent || 'unknown',
    'Sentiment': t.sentiment || 'neutral',
    'Priority': t.priority || 'low',
    'Status': t.status || 'new',
    'Escalated': t.escalate ? 'Yes' : 'No',
    'Assigned To': t.assigned_to || 'Unassigned',
    'Created': new Date(t.created_at).toLocaleString(),
    'Resolved': t.resolved_at ? new Date(t.resolved_at).toLocaleString() : 'N/A',
    'Summary': t.ticket_summary || '',
  }));

  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Tickets');
  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
  
  const blob = new Blob([wbout], { type: 'application/octet-stream' });
  saveAs(blob, filename);
};

export const exportStatsToReport = (stats, filename = 'stats_report.json') => {
  const data = {
    generated: new Date().toISOString(),
    total_tickets: stats?.total_tickets || 0,
    open_tickets: stats?.status_breakdown?.new || 0,
    escalated: stats?.escalated_count || 0,
    escalation_rate: stats?.escalation_rate || 0,
    status_breakdown: stats?.status_breakdown || {},
    intent_breakdown: stats?.intent_breakdown || {},
  };
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  saveAs(blob, filename);
};