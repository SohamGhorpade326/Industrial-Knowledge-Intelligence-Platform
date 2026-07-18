// @ts-nocheck
import React, { useState, useCallback } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Chip, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, TextField, MenuItem, Select, FormControl, InputLabel,
  LinearProgress,
} from '@mui/material';
import { CloudUpload, Delete, Description, Search } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { uploadService } from '../services/upload';
import type { Document } from '../types';
import toast from 'react-hot-toast';

const categories = [
  { value: 'general', label: 'General' },
  { value: 'sop', label: 'SOP Manual' },
  { value: 'maintenance_manual', label: 'Maintenance Manual' },
  { value: 'safety_manual', label: 'Safety Manual' },
  { value: 'inspection_report', label: 'Inspection Report' },
  { value: 'calibration_certificate', label: 'Calibration Certificate' },
  { value: 'incident_report', label: 'Incident Report' },
  { value: 'vendor_manual', label: 'Vendor Manual' },
  { value: 'compliance_document', label: 'Compliance Document' },
];

const Upload: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('general');
  const [machineName, setMachineName] = useState('');
  const [filterCategory, setFilterCategory] = useState('');

  const loadDocuments = useCallback(async () => {
    try {
      const result = await uploadService.getDocuments({ search: search || undefined, category: filterCategory || undefined });
      setDocuments(result.documents);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  }, [search, filterCategory]);

  React.useEffect(() => { loadDocuments(); }, [loadDocuments]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    setUploadProgress(0);

    for (let i = 0; i < acceptedFiles.length; i++) {
      const file = acceptedFiles[i];
      try {
        setUploadProgress(((i + 0.5) / acceptedFiles.length) * 100);
        await uploadService.uploadDocument(file, { category, machine_name: machineName });
        toast.success(`Uploaded: ${file.name}`);
      } catch (err: any) {
        toast.error(`Failed: ${file.name} - ${err.response?.data?.detail || err.message}`);
      }
      setUploadProgress(((i + 1) / acceptedFiles.length) * 100);
    }

    setUploading(false);
    setUploadProgress(0);
    loadDocuments();
  }, [category, machineName, loadDocuments]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
    },
    maxSize: 50 * 1024 * 1024,
  });

  const handleDelete = async (id: number) => {
    try {
      await uploadService.deleteDocument(id);
      toast.success('Document deleted');
      loadDocuments();
    } catch (err) {
      toast.error('Failed to delete document');
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const statusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography  variant="h5" sx={{ fontWeight: 700 }}  gutterBottom>
        Document Management
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Upload, manage, and organize industrial documents
      </Typography>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle2" gutterBottom>Upload Settings</Typography>
              <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                <InputLabel>Category</InputLabel>
                <Select value={category} onChange={(e) => setCategory(e.target.value)} label="Category">
                  {categories.map((c) => (
                    <MenuItem key={c.value} value={c.value}>{c.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                fullWidth size="small" label="Machine Name" value={machineName}
                onChange={(e) => setMachineName(e.target.value)} sx={{ mb: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 8 }}>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'divider',
                borderRadius: 3,
                p: 5,
                textAlign: 'center',
                cursor: 'pointer',
                bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                transition: 'all 0.3s ease',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' },
              }}
            >
              <input {...getInputProps()} />
              <CloudUpload sx={{ fontSize: 56, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                or click to browse • PDF, DOCX, TXT, PNG, JPG (max 50MB)
              </Typography>
            </Box>
          </motion.div>
        </Grid>
      </Grid>

      {uploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={uploadProgress} sx={{ height: 6, borderRadius: 3 }} />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
            Uploading... {Math.round(uploadProgress)}%
          </Typography>
        </Box>
      )}

      <Card sx={{ mt: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
            <TextField
              variant="outlined"
              size="small" placeholder="Search documents..." value={search}
              onChange={(e) => setSearch(e.target.value)}
              // @ts-ignore
              InputProps={{ startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} /> }}
              sx={{ flex: 1, minWidth: 200 }}
            />
            <FormControl size="small" sx={{ minWidth: 160 }}>
              <InputLabel>Filter Category</InputLabel>
              <Select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)} label="Filter Category">
                <MenuItem value="">All</MenuItem>
                {categories.map((c) => (
                  <MenuItem key={c.value} value={c.value}>{c.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Filename</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Machine</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <AnimatePresence>
                  {documents.map((doc) => (
                    <motion.tr
                      key={doc.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      layout
                      style={{ display: 'table-row' }}
                    >
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Description sx={{ color: 'primary.main', fontSize: 20 }} />
                          <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                            {doc.original_filename}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell><Chip label={doc.category} size="small" sx={{ fontSize: '0.7rem' }} /></TableCell>
                      <TableCell><Typography variant="body2">{doc.machine_name || '-'}</Typography></TableCell>
                      <TableCell><Typography variant="body2">{formatSize(doc.file_size)}</Typography></TableCell>
                      <TableCell><Chip label={doc.processing_status} size="small" color={statusColor(doc.processing_status) as any} sx={{ fontSize: '0.7rem' }} /></TableCell>
                      <TableCell><Typography variant="body2">{new Date(doc.upload_date).toLocaleDateString()}</Typography></TableCell>
                      <TableCell align="right">
                        <IconButton size="small" color="error" onClick={() => handleDelete(doc.id)}>
                          <Delete fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </motion.tr>
                  ))}
                </AnimatePresence>
              </TableBody>
            </Table>
          </TableContainer>

          {documents.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Description sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
              <Typography color="text.secondary">No documents found. Upload your first document!</Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Upload;
