import React, {
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { createPortal } from 'react-dom';
import { Check, ChevronDown } from 'lucide-react';

export type SearchableSelectOption = { value: string; label: string };

type SearchableSelectProps = {
  options: SearchableSelectOption[];
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  inputPlaceholder?: string;
};

export const SearchableSelect: React.FC<SearchableSelectProps> = ({
  options,
  value,
  onChange,
  disabled,
  inputPlaceholder = 'Type to search…',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const listId = useId();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const prevOpen = useRef(false);

  const selected = useMemo(
    () => options.find((o) => o.value === value) ?? options[0],
    [options, value],
  );
  const selectedLabel = selected?.label ?? '';

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return options;
    return options.filter(
      (o) =>
        o.label.toLowerCase().includes(q) ||
        o.value.toLowerCase().includes(q),
    );
  }, [options, query]);

  const syncMenuPosition = useCallback(() => {
    const wrap = containerRef.current;
    const menu = menuRef.current;
    if (!wrap || !menu) return;
    const r = wrap.getBoundingClientRect();
    menu.style.position = 'fixed';
    menu.style.top = `${Math.round(r.bottom + 4)}px`;
    menu.style.left = `${Math.round(r.left)}px`;
    menu.style.width = `${Math.round(r.width)}px`;
    menu.style.zIndex = '10000';
  }, []);

  useLayoutEffect(() => {
    if (!open) return;
    syncMenuPosition();
    window.addEventListener('scroll', syncMenuPosition, true);
    window.addEventListener('resize', syncMenuPosition);
    return () => {
      window.removeEventListener('scroll', syncMenuPosition, true);
      window.removeEventListener('resize', syncMenuPosition);
    };
  }, [open, syncMenuPosition, filtered.length]);

  useEffect(() => {
    if (open && !prevOpen.current) {
      setQuery('');
    }
    prevOpen.current = open;
  }, [open]);

  useEffect(() => {
    if (!open) return;
    let onDoc: ((e: MouseEvent) => void) | undefined;
    const timer = window.setTimeout(() => {
      onDoc = (e: MouseEvent) => {
        const t = e.target as Node;
        if (containerRef.current?.contains(t)) return;
        if (menuRef.current?.contains(t)) return;
        setOpen(false);
        setQuery('');
      };
      document.addEventListener('mousedown', onDoc);
    }, 0);
    return () => {
      window.clearTimeout(timer);
      if (onDoc) document.removeEventListener('mousedown', onDoc);
    };
  }, [open]);

  if (!options.length || !selected) {
    return (
      <div className="input w-full bg-gray-50 text-gray-500 py-2">No options</div>
    );
  }

  const inputValue = open ? query : selectedLabel;

  const menu =
    open && typeof document !== 'undefined' ? (
      <div
        ref={menuRef}
        className="max-h-60 overflow-auto rounded-lg bg-white py-1 text-left text-sm shadow-lg ring-1 ring-black/5"
      >
        <ul id={listId} role="listbox" className="m-0 list-none p-0">
          {filtered.length === 0 ? (
            <li className="cursor-default select-none px-3 py-2 text-gray-500">
              No matches
            </li>
          ) : (
            filtered.map((opt) => {
              const isSelected = opt.value === value;
              return (
                <li
                  key={opt.value === '' ? '__all__' : opt.value}
                  role="option"
                  aria-selected={isSelected}
                  className="relative cursor-pointer select-none px-3 py-2 pr-8 text-gray-700 hover:bg-primary-50 hover:text-gray-900"
                  onMouseDown={(e) => {
                    e.preventDefault();
                    onChange(opt.value);
                    setOpen(false);
                    setQuery('');
                  }}
                >
                  <span
                    className={`block truncate ${isSelected ? 'font-medium' : 'font-normal'}`}
                  >
                    {opt.label}
                  </span>
                  {isSelected && (
                    <span className="pointer-events-none absolute inset-y-0 right-2 flex items-center text-primary-600">
                      <Check className="h-4 w-4 shrink-0" aria-hidden />
                    </span>
                  )}
                </li>
              );
            })
          )}
        </ul>
      </div>
    ) : null;

  return (
    <div ref={containerRef} className="relative w-full">
      <div className="relative">
        <input
          type="text"
          role="combobox"
          aria-expanded={open}
          aria-controls={listId}
          aria-autocomplete="list"
          disabled={disabled}
          className="input w-full pr-9"
          placeholder={inputPlaceholder}
          value={inputValue}
          onChange={(e) => {
            setOpen(true);
            setQuery(e.target.value);
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={(e) => {
            if (e.key === 'Escape') {
              e.stopPropagation();
              setOpen(false);
              setQuery('');
              (e.target as HTMLInputElement).blur();
            }
          }}
        />
        <button
          type="button"
          tabIndex={-1}
          disabled={disabled}
          className="absolute inset-y-0 right-0 flex items-center pr-2 text-gray-400 hover:text-gray-600 disabled:opacity-50"
          aria-label={open ? 'Close list' : 'Open list'}
          onMouseDown={(e) => {
            e.preventDefault();
            e.stopPropagation();
          }}
          onClick={() => {
            if (disabled) return;
            setOpen((o) => !o);
          }}
        >
          <ChevronDown className="h-4 w-4 shrink-0" aria-hidden />
        </button>
      </div>
      {menu ? createPortal(menu, document.body) : null}
    </div>
  );
};
