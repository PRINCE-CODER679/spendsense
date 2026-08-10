import axios from 'axios';

const API_BASE_URL = '/api';

export const uploadService = {
  async previewStatement(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_BASE_URL}/upload/statement`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async confirmImport(transactions) {
    const response = await axios.post(`${API_BASE_URL}/upload/confirm`, {
      transactions,
    });
    return response.data;
  },

  downloadSampleStatement() {
    // Create a sample CSV content
    const sampleContent = `Date,Description,Debit,Credit
2026-08-01,SWIGGY ORDER 12345,450,
2026-08-02,SALARY CREDIT,,45000
2026-08-03,UBER INDIA TRIP 8921,280,
2026-08-04,NETFLIX.COM MONTHLY SUBSCRIPTION,649,
2026-08-05,DMART GROCERIES WEEKLY SHOPPING,1200,
2026-08-06,AMAZON PURCHASE ORDER #45678,2500,
2026-08-07,STARBUCKS COFFEE,350,
2026-08-08,PHONEPE TRANSFER TO FRIEND,5000,
2026-08-09,ELECTRICITY BILL PAYMENT,1850,
2026-08-10,GAS CYLINDER REFILL,850`;

    const blob = new Blob([sampleContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_bank_statement.csv';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
};
