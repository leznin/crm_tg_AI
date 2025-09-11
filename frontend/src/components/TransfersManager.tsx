import React, { useState, useMemo } from 'react';
import { useAppContext } from '../context/AppContext';
import { TransferRecord, Account } from '../types';
import { Search, Plus, X, Users, Link2, Trash2, Edit3, RefreshCcw } from 'lucide-react';

const statusLabels: Record<TransferRecord['status'], string> = {
  new: 'Новый',
  in_progress: 'В работе',
  completed: 'Завершен',
  cancelled: 'Отменен'
};

const statusColors: Record<TransferRecord['status'], string> = {
  new: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800'
};

interface TransferFormState {
  supplier_account_id: number | '';
  client_account_id: number | '';
  status: TransferRecord['status'];
  notes: string;
}

const TransfersManager: React.FC = () => {
  const {
    accounts,
    transferRecords,
    addTransferRecord,
    updateTransferRecord,
    deleteTransferRecord
  } = useAppContext();

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | TransferRecord['status']>('all');
  const [sortBy, setSortBy] = useState<'created_desc' | 'created_asc' | 'client' | 'supplier' | 'status'>('created_desc');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editing, setEditing] = useState<TransferRecord | null>(null);

  const [form, setForm] = useState<TransferFormState>({
    supplier_account_id: '',
    client_account_id: '',
    status: 'new',
    notes: ''
  });
  const [formError, setFormError] = useState<string | null>(null);

  const resetForm = () => {
    setForm({ supplier_account_id: '', client_account_id: '', status: 'new', notes: '' });
    setEditing(null);
    setIsFormOpen(false);
    setFormError(null);
  };

  const supplierOptions = useMemo(() => accounts.filter(a => a.category === 'partner' || a.category === 'client' || a.category === 'other'), [accounts]);
  const clientOptions = useMemo(() => accounts.filter(a => a.category === 'lead' || a.category === 'client'), [accounts]);

  const filtered = transferRecords.filter(r => {
    if (statusFilter !== 'all' && r.status !== statusFilter) return false;
    if (!search) return true;
    const supplier = accounts.find(a => a.id === r.supplier_account_id);
    const client = accounts.find(a => a.id === r.client_account_id);
    const s = search.toLowerCase();
    return [supplier, client].some(acc => acc && (
      (acc.first_name || '').toLowerCase().includes(s) ||
      (acc.last_name || '').toLowerCase().includes(s) ||
      (acc.username || '').toLowerCase().includes(s)
    ));
  }).sort((a, b) => {
    switch (sortBy) {
      case 'created_desc':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      case 'created_asc':
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      case 'client': {
        const ca = accounts.find(acc => acc.id === a.client_account_id);
        const cb = accounts.find(acc => acc.id === b.client_account_id);
        return (ca?.first_name || '').localeCompare(cb?.first_name || '');
      }
      case 'supplier': {
        const sa = accounts.find(acc => acc.id === a.supplier_account_id);
        const sb = accounts.find(acc => acc.id === b.supplier_account_id);
        return (sa?.first_name || '').localeCompare(sb?.first_name || '');
      }
      case 'status':
        const order: TransferRecord['status'][] = ['new','in_progress','completed','cancelled'];
        return order.indexOf(a.status) - order.indexOf(b.status);
      default:
        return 0;
    }
  });

  const counts = useMemo(() => transferRecords.reduce((acc, r) => {
    acc[r.status] = (acc[r.status] || 0) + 1;
    return acc;
  }, {} as Record<TransferRecord['status'], number>), [transferRecords]);

  const formatRelative = (dateStr: string) => {
    const diffMs = Date.now() - new Date(dateStr).getTime();
    const m = Math.floor(diffMs / 60000);
    if (m < 1) return 'только что';
    if (m < 60) return m + ' мин назад';
    const h = Math.floor(m / 60);
    if (h < 24) return h + ' ч назад';
    const d = Math.floor(h / 24);
    if (d < 7) return d + ' дн назад';
    const w = Math.floor(d / 7);
    if (w < 5) return w + ' нед назад';
    return new Date(dateStr).toLocaleDateString('ru-RU');
  };

  const renderStars = (rating?: number) => {
    if (rating == null) return null;
    return (
      <div className="flex gap-0.5">
        {Array.from({ length: 5 }, (_, i) => (
          <span key={i} className={`w-3 h-3 ${i < rating ? 'text-yellow-400' : 'text-gray-300'}`}>★</span>
        ))}
      </div>
    );
  };

  const cycleStatus = (record: TransferRecord) => {
    const order: TransferRecord['status'][] = ['new','in_progress','completed','cancelled'];
    const idx = order.indexOf(record.status);
    const next = order[(idx + 1) % order.length];
    updateTransferRecord(record.id, { status: next });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!form.supplier_account_id || !form.client_account_id) {
      setFormError('Выберите клиента и поставщика');
      return;
    }
    if (form.supplier_account_id === form.client_account_id) {
      setFormError('Клиент и поставщик не могут совпадать');
      return; // simple guard
    }
    if (editing) {
      updateTransferRecord(editing.id, {
        supplier_account_id: form.supplier_account_id as number,
        client_account_id: form.client_account_id as number,
        status: form.status,
        notes: form.notes
      });
    } else {
      addTransferRecord({
        supplier_account_id: form.supplier_account_id as number,
        client_account_id: form.client_account_id as number,
        status: form.status,
        notes: form.notes
      });
    }
    resetForm();
  };

  const startEdit = (record: TransferRecord) => {
    setEditing(record);
    setForm({
      supplier_account_id: record.supplier_account_id,
      client_account_id: record.client_account_id,
      status: record.status,
      notes: record.notes || ''
    });
    setIsFormOpen(true);
  };

  const accountLabel = (acc?: Account) => {
    if (!acc) return 'Не найден';
    const nameParts = [acc.first_name, acc.last_name].filter(Boolean).join(' ').trim();
    if (nameParts) return `${nameParts}${acc.username ? ' (@' + acc.username + ')' : ''}`;
    if (acc.username) return '@' + acc.username;
    return 'Без имени';
  };

  return (
  <div className="flex-1 flex flex-col bg-surface-0 text-gray-200 overflow-hidden">
      {/* Header / Filters */}
  <div className="bg-surface-50/70 backdrop-blur-md border-b border-white/5 p-4 lg:p-5 shadow-elevated-sm">
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Link2 className="w-6 h-6 text-cyan-400" />
              <h1 className="text-2xl lg:text-3xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-cyan-300 via-blue-300 to-purple-300">CRM Передачи</h1>
              <span className="text-xs font-medium px-2 py-1 rounded-full bg-surface-100/70 border border-white/5 text-gray-400 hidden sm:inline">{filtered.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => { setIsFormOpen(true); setEditing(null); }}
                className="px-3 py-2 rounded-lg flex items-center gap-2 text-sm bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white shadow-glow-blue hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 transition-all"
              >
                <Plus className="w-4 h-4" />
                <span className="hidden sm:inline">Новая</span>
              </button>
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1 min-w-0">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-4 h-4" />
              <input
                type="text"
                placeholder="Поиск по аккаунтам..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 text-base placeholder:text-gray-500"
              />
            </div>
            {/* Status Pills */}
            <div className="flex flex-wrap items-center gap-2">
              {([['all','Все'], ...Object.entries(statusLabels)] as [string,string][]).map(([key,label]) => {
                const active = statusFilter === key;
                return (
                  <button
                    key={key}
                    onClick={() => setStatusFilter(key as any)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${active ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 border-blue-500/40 text-white shadow-glow-blue' : 'bg-surface-100/60 border-white/5 text-gray-400 hover:bg-surface-100/80 hover:text-gray-200'}`}
                  >
                    {label}{key !== 'all' && counts[key as TransferRecord['status']] ? ` (${counts[key as TransferRecord['status']]})` : ''}
                  </button>
                );
              })}
            </div>
            <div className="flex items-center gap-2">
              <select
                value={sortBy}
                onChange={e => setSortBy(e.target.value as any)}
                className="px-3 py-2 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 text-sm"
              >
                <option value="created_desc">Новые сверху</option>
                <option value="created_asc">Старые сверху</option>
                <option value="client">По клиенту</option>
                <option value="supplier">По поставщику</option>
                <option value="status">По статусу</option>
              </select>
            </div>
          </div>
          {/* Status overview bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            {Object.entries(statusLabels).map(([k,label]) => (
              <div key={k} className="flex items-center justify-between rounded-md px-2 py-1 bg-surface-100/70 border border-white/5">
                <span className="text-gray-400 truncate font-medium">{label}</span>
                <span className="font-semibold text-gray-200">{counts[k as TransferRecord['status']] || 0}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Grid List */}
  <div className="flex-1 overflow-y-auto p-4 lg:p-6">
        {filtered.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
            {filtered.map(rec => {
              const supplier = accounts.find(a => a.id === rec.supplier_account_id);
              const client = accounts.find(a => a.id === rec.client_account_id);
              return (
                <div key={rec.id} className="rounded-lg p-4 lg:p-5 bg-surface-100/60 backdrop-blur-md border border-white/5 shadow-elevated-sm hover:shadow-elevated transition-shadow flex flex-col group">
                  {/* Top Row */}
                  <div className="flex items-start justify-between mb-2">
                    <button onClick={() => cycleStatus(rec)} className={`px-2 py-0.5 rounded-full text-xs font-semibold tracking-wide border shadow-inner-glow ${statusColors[rec.status]} transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/60`} title="Кликните чтобы сменить статус по кругу">
                      {statusLabels[rec.status]}
                    </button>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => startEdit(rec)} className="p-1.5 text-gray-500 hover:text-blue-300 hover:bg-white/5 rounded-md transition-colors" title="Редактировать"><Edit3 className="w-4 h-4" /></button>
                      <button onClick={() => deleteTransferRecord(rec.id)} className="p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded-md transition-colors" title="Удалить"><Trash2 className="w-4 h-4" /></button>
                    </div>
                  </div>
                  {/* Client & Supplier */}
                  <div className="flex flex-col gap-3 flex-1">
                    <div className="rounded-md p-2 bg-surface-200/50 border border-white/5">
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-medium text-gray-200 text-sm truncate" title={accountLabel(client)}>{accountLabel(client)}</span>
                        {client && <span className="text-[11px] px-1.5 py-0.5 rounded bg-blue-600/30 text-blue-300 font-medium border border-blue-500/30">Клиент</span>}
                      </div>
                      {client && (
                        <div className="mt-1 flex items-center justify-between text-[11px] text-gray-500">
                          <span>{client.category}</span>
                          <span>{renderStars(client.rating)}</span>
                        </div>
                      )}
                      {client && (
                        <div className="mt-1 text-[11px] text-gray-500 flex justify-between">
                          <span>Сообщ.: {client.total_messages}</span>
                          <span>Контакт: {new Date(client.last_contact).toLocaleDateString('ru-RU')}</span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center justify-center text-gray-600 text-xs -my-1">⇅</div>
                    <div className="rounded-md p-2 bg-surface-200/50 border border-white/5">
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-medium text-gray-200 text-sm truncate" title={accountLabel(supplier)}>{accountLabel(supplier)}</span>
                        {supplier && <span className="text-[11px] px-1.5 py-0.5 rounded bg-purple-600/30 text-purple-300 font-medium border border-purple-500/30">Поставщик</span>}
                      </div>
                      {supplier && (
                        <div className="mt-1 flex items-center justify-between text-[11px] text-gray-500">
                          <span>{supplier.category}</span>
                          <span>{renderStars(supplier.rating)}</span>
                        </div>
                      )}
                      {supplier && (
                        <div className="mt-1 text-[11px] text-gray-500 flex justify-between">
                          <span>Сообщ.: {supplier.total_messages}</span>
                          <span>Контакт: {new Date(supplier.last_contact).toLocaleDateString('ru-RU')}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  {/* Notes */}
                  {rec.notes && (
                    <p className="text-xs text-gray-400 mt-3 line-clamp-3" title={rec.notes}>{rec.notes}</p>
                  )}
                  {/* Footer */}
                  <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between text-[11px] text-gray-500">
                    <span>{formatRelative(rec.created_at)}</span>
                    <span>{new Date(rec.created_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {filtered.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-300 mb-2">Записей нет</h3>
            <p className="text-gray-500 mb-4">Создайте первую передачу</p>
            <button
              onClick={() => { setIsFormOpen(true); setEditing(null); }}
              className="px-6 py-2 rounded-lg bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white text-base shadow-glow-blue hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500 transition-all"
            >
              Новая передача
            </button>
          </div>
        )}
      </div>

      {/* Form Drawer / Modal */}
      {isFormOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-end md:items-center justify-center z-50">
          <div className="w-full md:max-w-xl md:rounded-xl p-6 shadow-elevated-lg max-h-[90vh] overflow-y-auto animate-scale-in bg-surface-50/80 border border-white/10 backdrop-blur-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-100">{editing ? 'Редактировать передачу' : 'Новая передача'}</h2>
              <button onClick={resetForm} className="p-2 text-gray-500 hover:text-gray-200 hover:bg-white/5 rounded-md"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium mb-1 text-gray-400">Клиент / Лид</label>
                <select
                  value={form.client_account_id}
                  onChange={e => { setForm(f => ({ ...f, client_account_id: e.target.value ? Number(e.target.value) : '' })); if (formError) setFormError(null); }}
                  className="w-full px-3 py-2 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 text-base"
                  required
                >
                  <option value="">Выберите</option>
                  {clientOptions.map(a => (
                    <option key={a.id} value={a.id}>{accountLabel(a)}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium mb-1 text-gray-400">Поставщик</label>
                <select
                  value={form.supplier_account_id}
                  onChange={e => { setForm(f => ({ ...f, supplier_account_id: e.target.value ? Number(e.target.value) : '' })); if (formError) setFormError(null); }}
                  className="w-full px-3 py-2 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 text-base"
                  required
                >
                  <option value="">Выберите</option>
                  {supplierOptions.map(a => (
                    <option key={a.id} value={a.id}>{accountLabel(a)}</option>
                  ))}
                </select>
              </div>

              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block text-xs font-medium mb-1 text-gray-400">Статус</label>
                  <select
                    value={form.status}
                    onChange={e => setForm(f => ({ ...f, status: e.target.value as TransferRecord['status'] }))}
                    className="w-full px-3 py-2 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 text-base"
                  >
                    {Object.entries(statusLabels).map(([k, v]) => (
                      <option key={k} value={k}>{v}</option>
                    ))}
                  </select>
                </div>
                {editing && (
                  <div className="flex items-end">
                    <button type="button" onClick={() => updateTransferRecord(editing.id, { status: 'new' })} className="flex items-center gap-1 px-3 py-2 text-xs rounded-md text-gray-400 hover:text-gray-200 bg-surface-100/60 hover:bg-surface-100/80 border border-white/5 transition-colors"><RefreshCcw className="w-4 h-4" />Сбросить</button>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-xs font-medium mb-1 text-gray-400">Заметки</label>
                <textarea
                  value={form.notes}
                  onChange={e => { setForm(f => ({ ...f, notes: e.target.value })); if (formError) setFormError(null); }}
                  rows={3}
                  className="w-full px-3 py-2 rounded-lg bg-surface-100/60 border border-white/5 focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60 resize-none text-base placeholder:text-gray-500"
                  placeholder="Короткие детали..."
                />
              </div>

              {formError && (
                <div className="text-sm text-red-400 bg-red-400/10 border border-red-400/30 rounded-md px-3 py-2">
                  {formError}
                </div>
              )}

              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={resetForm} className="px-4 py-2 rounded-lg border border-white/10 text-gray-400 hover:text-gray-200 hover:bg-white/5">Отмена</button>
                <button
                  type="submit"
                  disabled={!form.client_account_id || !form.supplier_account_id || form.client_account_id === form.supplier_account_id}
                  className={`px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white text-base shadow-glow-blue transition-all ${(!form.client_account_id || !form.supplier_account_id || form.client_account_id === form.supplier_account_id) ? 'opacity-50 cursor-not-allowed' : 'hover:from-blue-500 hover:via-indigo-500 hover:to-purple-500'}`}
                >
                  {editing ? 'Сохранить' : 'Создать'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransfersManager;
