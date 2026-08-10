import { useState } from 'react';
import { Download, ArrowRight, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import UploadDropzone from '../components/UploadDropzone';
import StatementPreviewTable from '../components/StatementPreviewTable';
import TransactionForm from '../components/TransactionForm';
import { uploadService } from '../services/uploadService';

const Upload = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setError(null);
    setPreviewData(null);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setError(null);
    setPreviewData(null);
  };

  const handleProcessFile = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setError(null);

    try {
      const result = await uploadService.previewStatement(selectedFile);
      setPreviewData(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process file. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleEditTransaction = (index) => {
    setEditingTransaction({ index, ...previewData.transactions[index] });
    setIsFormOpen(true);
  };

  const handleFormSubmit = (formData) => {
    const updatedTransactions = [...previewData.transactions];
    updatedTransactions[editingTransaction.index] = {
      ...updatedTransactions[editingTransaction.index],
      ...formData
    };
    setPreviewData({ ...previewData, transactions: updatedTransactions });
    setIsFormOpen(false);
    setEditingTransaction(null);
  };

  const handleConfirmImport = async () => {
    if (!previewData) return;

    setIsImporting(true);
    setError(null);

    try {
      // Filter out duplicates and invalid transactions
      const transactionsToImport = previewData.transactions.filter(
        t => !t.is_duplicate && !t.error
      );

      const result = await uploadService.confirmImport(transactionsToImport);

      if (result.success) {
        // Navigate to transactions page
        navigate('/transactions', {
          state: {
            importSuccess: true,
            importedCount: result.imported,
            skippedCount: result.skipped
          }
        });
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to import transactions. Please try again.');
    } finally {
      setIsImporting(false);
    }
  };

  const handleDownloadSample = () => {
    uploadService.downloadSampleStatement();
  };

  const validTransactions = previewData?.transactions?.filter(t => !t.is_duplicate && !t.error) || [];
  const duplicateTransactions = previewData?.transactions?.filter(t => t.is_duplicate) || [];
  const invalidTransactions = previewData?.transactions?.filter(t => t.error) || [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Upload Statement</h1>
          <p className="text-gray-600 mt-1">Import your bank statements to track transactions</p>
        </div>
        <button
          onClick={handleDownloadSample}
          className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <Download className="w-5 h-5" />
          Download Sample
        </button>
      </div>

      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <UploadDropzone
          onFileSelect={handleFileSelect}
          onRemove={handleRemoveFile}
          selectedFile={selectedFile}
        />

        {selectedFile && !previewData && (
          <div className="mt-4 flex justify-end">
            <button
              onClick={handleProcessFile}
              disabled={isProcessing}
              className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? 'Processing...' : (
                <>
                  Process Statement
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}
      </div>

      {/* Preview Section */}
      {previewData && (
        <>
          {/* Summary */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Processing Summary</h2>
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Total Rows</p>
                <p className="text-2xl font-bold text-gray-900">{previewData.total_rows}</p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Valid</p>
                <p className="text-2xl font-bold text-green-600">{previewData.valid_rows}</p>
              </div>
              <div className="bg-yellow-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Duplicates</p>
                <p className="text-2xl font-bold text-yellow-600">{previewData.duplicate_rows}</p>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Invalid</p>
                <p className="text-2xl font-bold text-red-600">{previewData.invalid_rows}</p>
              </div>
            </div>

            {previewData.errors.length > 0 && (
              <div className="mt-4 p-4 bg-red-50 rounded-lg">
                <h3 className="font-medium text-red-900 mb-2">Processing Errors:</h3>
                <ul className="text-sm text-red-700 space-y-1">
                  {previewData.errors.slice(0, 5).map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                  {previewData.errors.length > 5 && (
                    <li>...and {previewData.errors.length - 5} more errors</li>
                  )}
                </ul>
              </div>
            )}
          </div>

          {/* Preview Table */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Transaction Preview</h2>
            <StatementPreviewTable
              transactions={previewData.transactions}
              onEdit={handleEditTransaction}
            />
          </div>

          {/* Import Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {validTransactions.length} transactions ready to import
                </h2>
                {duplicateTransactions.length > 0 && (
                  <p className="text-sm text-yellow-600 mt-1">
                    {duplicateTransactions.length} duplicate transactions will be skipped
                  </p>
                )}
                {invalidTransactions.length > 0 && (
                  <p className="text-sm text-red-600 mt-1">
                    {invalidTransactions.length} invalid transactions will be skipped
                  </p>
                )}
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setPreviewData(null);
                    setSelectedFile(null);
                  }}
                  className="px-6 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmImport}
                  disabled={isImporting || validTransactions.length === 0}
                  className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isImporting ? 'Importing...' : (
                    <>
                      <CheckCircle className="w-5 h-5" />
                      Import Transactions
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Transaction Form Modal */}
      <TransactionForm
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingTransaction(null);
        }}
        onSubmit={handleFormSubmit}
        initialData={editingTransaction}
      />
    </div>
  );
};

export default Upload;
