import React, { useEffect, useState } from 'react';
import { usersApi } from '../../api/endpoints';
import { User } from '../../types';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Modal } from '../ui/Modal';

type Props = {
  user: User | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
};

export const UserFormModal: React.FC<Props> = ({ user, isOpen, onClose, onSuccess }) => {
  const isEdit = !!user;
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [location, setLocation] = useState('');
  const [phone, setPhone] = useState('');
  const [role, setRole] = useState('viewer');
  const [isActive, setIsActive] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setError(null);
    if (user) {
      setEmail(user.email);
      setPassword('');
      setFullName(user.full_name || '');
      setLocation(user.location || '');
      setPhone(user.phone || '');
      setRole(user.role || 'viewer');
      setIsActive(user.is_active);
    } else {
      setEmail('');
      setPassword('');
      setFullName('');
      setLocation('');
      setPhone('');
      setRole('viewer');
      setIsActive(true);
    }
  }, [isOpen, user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email.trim()) {
      setError('Email is required.');
      return;
    }
    if (!isEdit && !password.trim()) {
      setError('Password is required for new users.');
      return;
    }
    setSubmitting(true);
    try {
      if (isEdit && user) {
        const body: Record<string, unknown> = {
          email: email.trim(),
          full_name: fullName.trim() || null,
          location: location.trim() || null,
          phone: phone.trim() || null,
          role,
          is_active: isActive,
        };
        if (password.trim()) {
          body.password = password.trim();
        }
        await usersApi.update(user.id, body);
      } else {
        await usersApi.create({
          email: email.trim(),
          password: password.trim(),
          full_name: fullName.trim() || null,
          location: location.trim() || null,
          phone: phone.trim() || null,
          role,
        });
      }
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const ax = err as { response?: { data?: { detail?: unknown } } };
      const d = ax.response?.data?.detail;
      const msg =
        typeof d === 'string'
          ? d
          : Array.isArray(d)
            ? d.map((x: { msg?: string }) => x.msg || JSON.stringify(x)).join('; ')
            : 'Could not save user.';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? 'Edit user' : 'Create user'}
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
            {error}
          </div>
        )}
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <Input
          label={isEdit ? 'New password (optional)' : 'Password'}
          type="password"
          autoComplete={isEdit ? 'new-password' : 'new-password'}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={isEdit ? 'Leave blank to keep current password' : ''}
        />
        <Input
          label="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
        />
        <Input label="Location" value={location} onChange={(e) => setLocation(e.target.value)} />
        <Input
          label="Phone"
          type="tel"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
          <select
            className="input w-full"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <option value="viewer">Viewer</option>
            <option value="researcher">Researcher</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        {isEdit && (
          <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
            />
            Active account
          </label>
        )}
        <p className="text-xs text-gray-500">
          Study access is managed separately with the <strong>Studies</strong> button on the user
          list after the account exists.
        </p>
        <div className="flex justify-end gap-2 pt-2 border-t border-gray-100">
          <Button type="button" variant="secondary" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button type="submit" disabled={submitting}>
            {submitting ? 'Saving…' : isEdit ? 'Save changes' : 'Create user'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
