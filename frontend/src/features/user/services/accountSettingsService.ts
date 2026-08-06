import { doc, getDoc, serverTimestamp, setDoc } from 'firebase/firestore';

import { db } from 'firebaseConfig';
import { isE2EMockAuthEnabled } from 'shared/e2e/e2eMockAuth';

import type { AccountSettingsDoc } from '../types/accountSettingsTypes';

export async function fetchAccountSettings(uid: string): Promise<AccountSettingsDoc | null> {
  if (isE2EMockAuthEnabled()) {
    return {
      name: 'E2E User',
      email: 'e2e@vetta.test',
    };
  }
  const snap = await getDoc(doc(db, 'users', uid));
  return snap.exists() ? (snap.data() as AccountSettingsDoc) : null;
}

export async function persistAccountSettings(
  uid: string,
  payload: {
    name?: string;
    email?: string;
    photoURL?: string;
  },
): Promise<void> {
  await setDoc(
    doc(db, 'users', uid),
    {
      ...payload,
      updatedAt: serverTimestamp(),
    },
    { merge: true },
  );
}
