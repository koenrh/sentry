import * as React from 'react';
import styled from '@emotion/styled';
import isArray from 'lodash/isArray';
import isNumber from 'lodash/isNumber';
import isString from 'lodash/isString';

import AnnotatedText from 'app/components/events/meta/annotatedText';
import ExternalLink from 'app/components/links/externalLink';
import {IconAdd, IconOpen, IconSubtract} from 'app/icons';
import {Meta} from 'app/types';
import {isUrl} from 'app/utils';

function looksLikeObjectRepr(value: string) {
  const a = value[0];
  const z = value[value.length - 1];
  if (a === '<' && z === '>') {
    return true;
  } else if (a === '[' && z === ']') {
    return true;
  } else if (a === '(' && z === ')') {
    return true;
  } else if (z === ')' && value.match(/^[\w\d._-]+\(/)) {
    return true;
  }
  return false;
}

function looksLikeMultiLineString(value: string) {
  return !!value.match(/[\r\n]/);
}

function padNumbersInString(string: string) {
  return string.replace(/(\d+)/g, (num: string) => {
    let isNegative = false;
    let realNum = parseInt(num, 10);
    if (realNum < 0) {
      realNum *= -1;
      isNegative = true;
    }
    let s = '0000000000000' + realNum;
    s = s.substr(s.length - (isNegative ? 11 : 12));
    if (isNegative) {
      s = '-' + s;
    }
    return s;
  });
}

function naturalCaseInsensitiveSort(a: string, b: string) {
  a = padNumbersInString(a).toLowerCase();
  b = padNumbersInString(b).toLowerCase();
  return a === b ? 0 : a < b ? -1 : 1;
}

function analyzeStringForRepr(value: string) {
  const rv = {
    repr: value,
    isString: true,
    isMultiLine: false,
    isStripped: false,
  };

  // stripped for security reasons
  if (value.match(/^['"]?\*{8,}['"]?$/)) {
    rv.isStripped = true;
    return rv;
  }

  if (looksLikeObjectRepr(value)) {
    rv.isString = false;
  } else {
    rv.isMultiLine = looksLikeMultiLineString(value);
  }

  return rv;
}

type ToggleWrapProps = {
  highUp: boolean;
  wrapClassName: string;
};

type ToggleWrapState = {
  toggled: boolean;
};

class ToggleWrap extends React.Component<ToggleWrapProps, ToggleWrapState> {
  state: ToggleWrapState = {toggled: false};

  render() {
    if (React.Children.count(this.props.children) === 0) {
      return null;
    }

    const {wrapClassName, children} = this.props;
    const wrappedChildren = <span className={wrapClassName}>{children}</span>;

    if (this.props.highUp) {
      return wrappedChildren;
    }

    return (
      <span>
        <ToggleIcon
          isOpen={this.state.toggled}
          href="#"
          onClick={evt => {
            this.setState(state => ({toggled: !state.toggled}));
            evt.preventDefault();
          }}
        >
          {this.state.toggled ? (
            <IconSubtract size="9px" color="white" />
          ) : (
            <IconAdd size="9px" color="white" />
          )}
        </ToggleIcon>
        {this.state.toggled && wrappedChildren}
      </span>
    );
  }
}

type Value = null | string | boolean | number | {[key: string]: Value} | Value[];

type Props = React.HTMLAttributes<HTMLPreElement> & {
  data: Value;
  preserveQuotes?: boolean;
  withAnnotatedText?: boolean;
  maxDefaultDepth?: number;
  meta?: Meta;
  jsonConsts?: boolean;
};

type State = {
  data: Value;
  withAnnotatedText: boolean;
};

class ContextData extends React.Component<Props, State> {
  static defaultProps = {
    data: null,
    withAnnotatedText: false,
  };

  renderValue(value: Value) {
    const {
      preserveQuotes,
      meta,
      withAnnotatedText,
      jsonConsts,
      maxDefaultDepth,
    } = this.props;
    const maxDepth = maxDefaultDepth ?? 2;

    function getValueWithAnnotatedText(v: Value, meta?: Meta) {
      return <AnnotatedText value={v} meta={meta} />;
    }

    /*eslint no-shadow:0*/
    function walk(value: Value, depth: number) {
      let i = 0;
      const children: React.ReactNode[] = [];
      if (value === null) {
        return <span className="val-null">{jsonConsts ? 'null' : 'None'}</span>;
      }

      if (value === true || value === false) {
        return (
          <span className="val-bool">
            {jsonConsts ? (value ? 'true' : 'false') : value ? 'True' : 'False'}
          </span>
        );
      }

      if (isString(value)) {
        const valueInfo = analyzeStringForRepr(value);

        const valueToBeReturned = withAnnotatedText
          ? getValueWithAnnotatedText(valueInfo.repr, meta)
          : valueInfo.repr;

        const out = [
          <span
            key="value"
            className={
              (valueInfo.isString ? 'val-string' : '') +
              (valueInfo.isStripped ? ' val-stripped' : '') +
              (valueInfo.isMultiLine ? ' val-string-multiline' : '')
            }
          >
            {preserveQuotes ? `"${valueToBeReturned}"` : valueToBeReturned}
          </span>,
        ];

        if (valueInfo.isString && isUrl(value)) {
          out.push(
            <ExternalLink key="external" href={value} className="external-icon">
              <StyledIconOpen size="xs" />
            </ExternalLink>
          );
        }

        return out;
      }

      if (isNumber(value)) {
        const valueToBeReturned =
          withAnnotatedText && meta ? getValueWithAnnotatedText(value, meta) : value;
        return <span>{valueToBeReturned}</span>;
      }

      if (isArray(value)) {
        for (i = 0; i < value.length; i++) {
          children.push(
            <span className="val-array-item" key={i}>
              {walk(value[i], depth + 1)}
              {i < value.length - 1 ? (
                <span className="val-array-sep">{', '}</span>
              ) : null}
            </span>
          );
        }
        return (
          <span className="val-array">
            <span className="val-array-marker">{'['}</span>
            <ToggleWrap highUp={depth <= maxDepth} wrapClassName="val-array-items">
              {children}
            </ToggleWrap>
            <span className="val-array-marker">{']'}</span>
          </span>
        );
      }

      if (React.isValidElement(value)) {
        return value;
      }

      const keys = Object.keys(value);
      keys.sort(naturalCaseInsensitiveSort);
      for (i = 0; i < keys.length; i++) {
        const key = keys[i];
        children.push(
          <span className="val-dict-pair" key={key}>
            <span className="val-dict-key">
              <span className="val-string">{preserveQuotes ? `"${key}"` : key}</span>
            </span>
            <span className="val-dict-col">{': '}</span>
            <span className="val-dict-value">
              {walk(value[key], depth + 1)}
              {i < keys.length - 1 ? <span className="val-dict-sep">{', '}</span> : null}
            </span>
          </span>
        );
      }
      return (
        <span className="val-dict">
          <span className="val-dict-marker">{'{'}</span>
          <ToggleWrap highUp={depth <= maxDepth - 1} wrapClassName="val-dict-items">
            {children}
          </ToggleWrap>
          <span className="val-dict-marker">{'}'}</span>
        </span>
      );
    }
    return walk(value, 0);
  }

  render() {
    const {
      data,
      preserveQuotes: _preserveQuotes,
      withAnnotatedText: _withAnnotatedText,
      meta: _meta,
      children,
      ...other
    } = this.props;

    return (
      <pre {...other}>
        {this.renderValue(data)}
        {children}
      </pre>
    );
  }
}

const StyledIconOpen = styled(IconOpen)`
  position: relative;
  top: 1px;
`;

const ToggleIcon = styled('a')<{isOpen?: boolean}>`
  display: inline-block;
  position: relative;
  top: 1px;
  height: 11px;
  width: 11px;
  line-height: 1;
  padding-left: 1px;
  margin-left: 1px;
  border-radius: 2px;

  background: ${p => (p.isOpen ? p.theme.gray300 : p.theme.blue300)};
  &:hover {
    background: ${p => (p.isOpen ? p.theme.gray400 : p.theme.blue200)};
  }
`;

export default ContextData;
