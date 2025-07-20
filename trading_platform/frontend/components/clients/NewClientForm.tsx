
'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

interface NewClientFormProps {
  onClose: () => void;
  onClientAdded: () => void;
}

export default function NewClientForm({ onClose, onClientAdded }: NewClientFormProps) {
  const [name, setName] = useState('');
  const [clientId, setClientId] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [apiSecret, setApiSecret] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [twoFa, setTwoFa] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const payload = {
      name,
      client_id: clientId,
      api_key: apiKey,
      api_secret: apiSecret,
      password: loginPassword,
      two_fa: twoFa,
    };

    const promise = fetch('/api/v1/clients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(async (response) => {
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add client');
      }
      return response.json();
    });

    toast.promise(promise, {
      loading: 'Adding new client...',
      success: () => {
        onClientAdded();
        onClose();
        return 'Client added successfully!';
      },
      error: (err) => {
        console.error("Error adding client:", err);
        return `Failed to add client: ${err instanceof Error ? err.message : 'Unknown error'}`;
      },
    }).finally(() => {
      setLoading(false);
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <Card className="p-8 w-full max-w-md bg-background relative">
        <h2 className="text-2xl font-bold mb-6">Add New Client</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-foreground">Client Name</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-foreground shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="clientId" className="block text-sm font-medium text-foreground">Client ID (MOFSL)</label>
            <input
              type="text"
              id="clientId"
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              required
              className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-foreground shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="apiKey" className="block text-sm font-medium text-foreground">API Key</label>
            <input
              type="text"
              id="apiKey"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              required
              className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-foreground shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="apiSecret" className="block text-sm font-medium text-foreground">API Secret Key</label>
            <input
              type="password"
              id="apiSecret"
              value={apiSecret}
              onChange={(e) => setApiSecret(e.target.value)}
              required
              className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-foreground shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="loginPassword" className="block text-sm font-medium text-foreground">Login Password</label>
            <input
              type="password"
              id="loginPassword"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              required
              className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-foreground shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="twoFa" className="block text-sm font-medium text-foreground">2FA (e.g., PAN, DOB)</label>
            <input
              type="text"
              id="twoFa"
              value={twoFa}
              onChange={(e) => setTwoFa(e.target.value)}
              required
              className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-foreground shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
            />
          </div>
          <div className="flex justify-end space-x-4 mt-6">
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Adding...' : 'Add Client'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
