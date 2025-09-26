'use client';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { VariantProps, cva } from 'class-variance-authority';
import {
  Locale,
  addDays,
  addMonths,
  addWeeks,
  addYears,
  differenceInMinutes,
  format,
  getMonth,
  isSameDay,
  isSameHour,
  isSameMonth,
  isToday,
  setHours,
  setMonth,
  startOfMonth,
  startOfWeek,
  subDays,
  subMonths,
  subWeeks,
  subYears,
} from 'date-fns';
import { enUS } from 'date-fns/locale/en-US';
import {
  ReactNode,
  createContext,
  forwardRef,
  useCallback,
  useContext,
  useMemo,
  useState,
  useEffect,
} from 'react';
import { useHotkeys } from 'react-hotkeys-hook';

const monthEventVariants = cva('size-2 rounded-full', {
  variants: {
    variant: {
      default: 'bg-primary',
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      pink: 'bg-pink-500',
      purple: 'bg-purple-500',
    },
  },
  defaultVariants: {
    variant: 'default',
  },
});

const dayEventVariants = cva('font-bold border-l-4 rounded p-2 text-xs', {
  variants: {
    variant: {
      default: 'bg-muted/30 text-muted-foreground border-muted',
      blue: 'bg-blue-500/30 text-blue-600 border-blue-500',
      green: 'bg-green-500/30 text-green-600 border-green-500',
      pink: 'bg-pink-500/30 text-pink-600 border-pink-500',
      purple: 'bg-purple-500/30 text-purple-600 border-purple-500',
    },
  },
  defaultVariants: {
    variant: 'default',
  },
});

type View = 'day' | 'week' | 'month' | 'year';

type ContextType = {
  view: View;
  setView: (view: View) => void;
  date: Date;
  setDate: (date: Date) => void;
  events: CalendarEvent[];
  locale: Locale;
  setEvents: (date: CalendarEvent[]) => void;
  onChangeView?: (view: View) => void;
  onEventClick?: (event: CalendarEvent) => void;
  enableHotkeys?: boolean;
  today: Date;
  selectedDate: Date | null;
  setSelectedDate: (date: Date | null) => void;
};

const Context = createContext<ContextType>({} as ContextType);

export type CalendarEvent = {
  id: string;
  start: Date;
  end: Date;
  title: string;
  color?: VariantProps<typeof monthEventVariants>['variant'];
};

type CalendarProps = {
  children: ReactNode;
  defaultDate?: Date;
  events?: CalendarEvent[];
  view?: View;
  locale?: Locale;
  enableHotkeys?: boolean;
  onChangeView?: (view: View) => void;
  onEventClick?: (event: CalendarEvent) => void;
  onDateSelect?: (date: Date) => void;
};

const Calendar = ({
  children,
  defaultDate = new Date(),
  locale = enUS,
  enableHotkeys = true,
  view: _defaultMode = 'month',
  onEventClick,
  events: defaultEvents = [],
  onChangeView,
  onDateSelect,
}: CalendarProps) => {
  const [view, setView] = useState<View>(_defaultMode);
  const [date, setDate] = useState(defaultDate);
  const [events, setEvents] = useState<CalendarEvent[]>(defaultEvents);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  useEffect(() => {
    // console.log("📅 [CALENDAR] defaultDate changée:", defaultDate);
    setDate(defaultDate);
  }, [defaultDate]);

  useEffect(() => {
    // console.log("📅 [CALENDAR] Mise à jour des événements:", defaultEvents.length);
    setEvents(defaultEvents);
  }, [defaultEvents]);

  const changeView = (view: View) => {
    setView(view);
    onChangeView?.(view);
  };

  useEffect(() => {
    if (selectedDate && onDateSelect) {
      onDateSelect(selectedDate);
    }
  }, [selectedDate, onDateSelect]);

  useHotkeys('m', () => changeView('month'), {
    enabled: enableHotkeys,
  });

  useHotkeys('w', () => changeView('week'), {
    enabled: enableHotkeys,
  });

  useHotkeys('y', () => changeView('year'), {
    enabled: enableHotkeys,
  });

  useHotkeys('d', () => changeView('day'), {
    enabled: enableHotkeys,
  });

  return (
    <Context.Provider
      value={{
        view,
        setView: changeView,
        date,
        setDate,
        events,
        setEvents,
        locale,
        enableHotkeys,
        onEventClick,
        onChangeView,
        today: new Date(),
        selectedDate,
        setSelectedDate,
      }}
    >
      {children}
    </Context.Provider>
  );
};

export const useCalendar = () => useContext(Context);

const CalendarViewTrigger = forwardRef<
  HTMLButtonElement,
  React.HTMLAttributes<HTMLButtonElement> & {
    view: View;
  }
>(({ children, view, ...props }, ref) => {
  const { view: currentView, setView, onChangeView } = useCalendar();

  return (
    <Button
      aria-current={currentView === view}
      size="sm"
      variant="ghost"
      ref={ref}
      {...props}
      onClick={() => {
        setView(view);
        onChangeView?.(view);
      }}
    >
      {children}
    </Button>
  );
});
CalendarViewTrigger.displayName = 'CalendarViewTrigger';

const EventGroup = ({
  events,
  hour,
}: {
  events: CalendarEvent[];
  hour: Date;
}) => {
  return (
    <div className="h-20 border-t last:border-b">
      {events
        .filter((event) => isSameHour(event.start, hour))
        .map((event) => {
          const hoursDifference =
            differenceInMinutes(event.end, event.start) / 60;
          const startPosition = event.start.getMinutes() / 60;

          return (
            <div
              key={event.id}
              className={cn(
                'relative',
                dayEventVariants({ variant: event.color })
              )}
              style={{
                top: `${startPosition * 100}%`,
                height: `${hoursDifference * 100}%`,
              }}
            >
              {event.title}
            </div>
          );
        })}
    </div>
  );
};

const CalendarDayView = () => {
  const { view, events, date } = useCalendar();

  if (view !== 'day') return null;

  const hours = [...Array(24)].map((_, i) => setHours(date, i));

  return (
    <div className="flex relative pt-2 overflow-auto h-full">
      <TimeTable />
      <div className="flex-1">
        {hours.map((hour) => (
          <EventGroup key={hour.toString()} hour={hour} events={events} />
        ))}
      </div>
    </div>
  );
};

const CalendarWeekView = () => {
  const { view, date, events, locale, setSelectedDate, selectedDate } = useCalendar();

  const weekDates = useMemo(() => {
    const dates = [];
    const startDate = startOfWeek(date, { weekStartsOn: 1 });

    for (let i = 0; i < 7; i++) {
      dates.push(addDays(startDate, i));
    }

    return dates;
  }, [date]);

  if (view !== 'week') return null;
  
  const handleDateClick = (clickedDate: Date) => {
    setSelectedDate(clickedDate);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="grid grid-cols-8 h-6 border-b">
        <div />
        {weekDates.map((weekDate) => {
          const isCurrentDate = isToday(weekDate);
          const isSelectedDay = selectedDate ? isSameDay(weekDate, selectedDate) : false;
          
          return (
            <div
              key={weekDate.toString()}
              className={cn(
                'text-center text-sm sticky top-0 bg-background cursor-pointer',
                isCurrentDate && 'text-primary font-bold',
                isSelectedDay && 'bg-primary/5'
              )}
              onClick={() => handleDateClick(weekDate)}
            >
              <div className="flex flex-col justify-center items-center">
                <div>{format(weekDate, 'EEE', { locale })}</div>
                <div
                  className={cn(
                    'size-6 grid place-content-center rounded-full',
                    isCurrentDate && 'bg-primary text-primary-foreground',
                    isSelectedDay && !isCurrentDate && 'border-2 border-primary'
                  )}
                >
                  {format(weekDate, 'd')}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="flex-1">
        <div className="w-fit">
          <TimeTable />
        </div>
        <div className="grid grid-cols-7 flex-1">
          {weekDates.map((weekDate, i) => {
            // Création des heures pour chaque jour de la semaine
            const hoursForDay = [...Array(24)].map((_, hourIndex) => {
              const hourDate = new Date(weekDate);
              hourDate.setHours(hourIndex, 0, 0, 0);
              return hourDate;
            });
            
            return (
              <div
                className={cn(
                  'h-full text-sm text-muted-foreground border-l first:border-l-0',
                  [0, 6].includes(i) && 'bg-muted/50'
                )}
                key={weekDate.toString()}
              >
                {hoursForDay.map((hour) => (
                  <EventGroup
                    key={hour.toString()}
                    hour={hour}
                    events={events}
                  />
                ))}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const CalendarMonthView = () => {
  const { date, view, events, locale, setSelectedDate, selectedDate } = useCalendar();

  // Journalisation de débogage
  // console.log("📅 [MONTH-VIEW] Rendu avec", events.length, "événements");
  // if (events.length > 0) {
  //   console.log("📅 [MONTH-VIEW] Premier événement:", {
  //     id: events[0].id,
  //     title: events[0].title,
  //     start: events[0].start.toISOString(),
  //     end: events[0].end.toISOString()
  //   });
  // }

  const monthDates = useMemo(() => getDaysInMonth(date), [date]);
  const weekDays = useMemo(() => generateWeekdays(locale), [locale]);

  if (view !== 'month') return null;
  
  const handleDateClick = (clickedDate: Date) => {
    // console.log("📅 [MONTH-VIEW] Date cliquée:", clickedDate.toISOString());
    setSelectedDate(clickedDate);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="grid grid-cols-7 gap-px sticky top-0 bg-background border-b">
        {weekDays.map((day, i) => (
          <div
            key={day}
            className={cn(
              'mb-2 text-right text-sm text-muted-foreground pr-2',
              [0, 6].includes(i) && 'text-muted-foreground/50'
            )}
          >
            {day}
          </div>
        ))}
      </div>
      <div className="grid overflow-hidden -mt-px flex-1 auto-rows-fr p-px grid-cols-7 gap-px">
        {monthDates.map((_date) => {
          const currentEvents = events.filter((event) =>
            isSameDay(event.start, _date)
          );
          
          // Débogage des événements pour ce jour
          // if (currentEvents.length > 0) {
          //   console.log(`📅 [MONTH-VIEW] Jour ${format(_date, 'yyyy-MM-dd')} a ${currentEvents.length} événements:`, 
          //     currentEvents.map(e => ({ id: e.id, title: e.title }))
          //   );
          // }
          
          const isSelected = selectedDate ? isSameDay(_date, selectedDate) : false;

          return (
            <div
              className={cn(
                'ring-1 p-2 text-sm text-muted-foreground ring-border overflow-auto cursor-pointer transition-colors',
                !isSameMonth(date, _date) && 'text-muted-foreground/50',
                isSelected && 'ring-2 ring-primary bg-primary/5'
              )}
              key={_date.toString()}
              onClick={() => handleDateClick(_date)}
            >
              <span
                className={cn(
                  'size-6 grid place-items-center rounded-full mb-1 sticky top-0',
                  isToday(_date) && 'bg-primary text-primary-foreground',
                  isSelected && !isToday(_date) && 'border-2 border-primary'
                )}
              >
                {format(_date, 'd')}
              </span>

              {currentEvents.map((event) => {
                return (
                  <div
                    key={event.id}
                    className="px-1 rounded text-sm flex items-center gap-1"
                  >
                    <div
                      className={cn(
                        'shrink-0',
                        monthEventVariants({ variant: event.color })
                      )}
                    ></div>
                    <span className="flex-1 truncate">{event.title}</span>
                    <time className="tabular-nums text-muted-foreground/50 text-xs">
                      {format(event.start, 'HH:mm')}
                    </time>
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
};

const CalendarYearView = () => {
  const { view, date, today, locale } = useCalendar();

  const months = useMemo(() => {
    if (!view) {
      return [];
    }

    return Array.from({ length: 12 }).map((_, i) => {
      return getDaysInMonth(setMonth(date, i));
    });
  }, [date, view]);

  const weekDays = useMemo(() => generateWeekdays(locale), [locale]);

  if (view !== 'year') return null;

  return (
    <div className="grid grid-cols-4 gap-10 overflow-auto h-full">
      {months.map((days, i) => (
        <div key={days[0].toString()}>
          <span className="text-xl">{i + 1}</span>

          <div className="grid grid-cols-7 gap-2 my-5">
            {weekDays.map((day) => (
              <div
                key={day}
                className="text-center text-xs text-muted-foreground"
              >
                {day}
              </div>
            ))}
          </div>

          <div className="grid gap-x-2 text-center grid-cols-7 text-xs tabular-nums">
            {days.map((_date) => {
              return (
                <div
                  key={_date.toString()}
                  className={cn(
                    getMonth(_date) !== i && 'text-muted-foreground'
                  )}
                >
                  <div
                    className={cn(
                      'aspect-square grid place-content-center size-full tabular-nums',
                      isSameDay(today, _date) &&
                        getMonth(_date) === i &&
                        'bg-primary text-primary-foreground rounded-full'
                    )}
                  >
                    {format(_date, 'd')}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

const CalendarNextTrigger = forwardRef<
  HTMLButtonElement,
  React.HTMLAttributes<HTMLButtonElement>
>(({ children, onClick, ...props }, ref) => {
  const { date, setDate, view, enableHotkeys } = useCalendar();

  const next = useCallback(() => {
    if (view === 'day') {
      setDate(addDays(date, 1));
    } else if (view === 'week') {
      setDate(addWeeks(date, 1));
    } else if (view === 'month') {
      setDate(addMonths(date, 1));
    } else if (view === 'year') {
      setDate(addYears(date, 1));
    }
  }, [date, view, setDate]);

  useHotkeys('ArrowRight', () => next(), {
    enabled: enableHotkeys,
  });

  return (
    <Button
      size="icon"
      variant="outline"
      ref={ref}
      {...props}
      onClick={(e) => {
        next();
        onClick?.(e);
      }}
    >
      {children}
    </Button>
  );
});
CalendarNextTrigger.displayName = 'CalendarNextTrigger';

const CalendarPrevTrigger = forwardRef<
  HTMLButtonElement,
  React.HTMLAttributes<HTMLButtonElement>
>(({ children, onClick, ...props }, ref) => {
  const { date, setDate, view, enableHotkeys } = useCalendar();

  useHotkeys('ArrowLeft', () => prev(), {
    enabled: enableHotkeys,
  });

  const prev = useCallback(() => {
    if (view === 'day') {
      setDate(subDays(date, 1));
    } else if (view === 'week') {
      setDate(subWeeks(date, 1));
    } else if (view === 'month') {
      setDate(subMonths(date, 1));
    } else if (view === 'year') {
      setDate(subYears(date, 1));
    }
  }, [date, view, setDate]);

  return (
    <Button
      size="icon"
      variant="outline"
      ref={ref}
      {...props}
      onClick={(e) => {
        prev();
        onClick?.(e);
      }}
    >
      {children}
    </Button>
  );
});
CalendarPrevTrigger.displayName = 'CalendarPrevTrigger';

const CalendarTodayTrigger = forwardRef<
  HTMLButtonElement,
  React.HTMLAttributes<HTMLButtonElement>
>(({ children, onClick, ...props }, ref) => {
  const { setDate, enableHotkeys, today } = useCalendar();

  useHotkeys('t', () => jumpToToday(), {
    enabled: enableHotkeys,
  });

  const jumpToToday = useCallback(() => {
    setDate(today);
  }, [today, setDate]);

  return (
    <Button
      variant="outline"
      ref={ref}
      {...props}
      onClick={(e) => {
        jumpToToday();
        onClick?.(e);
      }}
    >
      {children}
    </Button>
  );
});
CalendarTodayTrigger.displayName = 'CalendarTodayTrigger';

const CalendarCurrentDate = () => {
  const { date, view } = useCalendar();

  return (
    <time dateTime={date.toISOString()} className="tabular-nums">
      {format(date, view === 'day' ? 'dd MMMM yyyy' : 'MMMM yyyy')}
    </time>
  );
};

const TimeTable = () => {
  const now = new Date();

  return (
    <div className="pr-2 w-12">
      {Array.from(Array(25).keys()).map((hour) => {
        return (
          <div
            className="text-right relative text-xs text-muted-foreground/50 h-20 last:h-0"
            key={hour}
          >
            {now.getHours() === hour && (
              <div
                className="absolute z- left-full translate-x-2 w-dvw h-[2px] bg-red-500"
                style={{
                  top: `${(now.getMinutes() / 60) * 100}%`,
                }}
              >
                <div className="size-2 rounded-full bg-red-500 absolute left-0 top-1/2 -translate-x-1/2 -translate-y-1/2"></div>
              </div>
            )}
            <p className="top-0 -translate-y-1/2">
              {hour === 24 ? 0 : hour}:00
            </p>
          </div>
        );
      })}
    </div>
  );
};

const getDaysInMonth = (date: Date) => {
  const startOfMonthDate = startOfMonth(date);
  const startOfWeekForMonth = startOfWeek(startOfMonthDate, {
    weekStartsOn: 0,
  });

  let currentDate = startOfWeekForMonth;
  const calendar = [];

  while (calendar.length < 42) {
    calendar.push(new Date(currentDate));
    currentDate = addDays(currentDate, 1);
  }

  return calendar;
};

const generateWeekdays = (locale: Locale) => {
  const daysOfWeek = [];
  for (let i = 0; i < 7; i++) {
    const date = addDays(startOfWeek(new Date(), { weekStartsOn: 0 }), i);
    daysOfWeek.push(format(date, 'EEEEEE', { locale }));
  }
  return daysOfWeek;
};

export {
  Calendar,
  CalendarCurrentDate,
  CalendarDayView,
  CalendarMonthView,
  CalendarNextTrigger,
  CalendarPrevTrigger,
  CalendarTodayTrigger,
  CalendarViewTrigger,
  CalendarWeekView,
  CalendarYearView,
};